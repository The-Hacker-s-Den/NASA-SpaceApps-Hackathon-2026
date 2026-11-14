"""
Lahore-Specific Weather AI Training Pipeline
=============================================
Extracts Lahore data from the 2000-2026 4-hour dataset and retrains
the Prithvi-Informed PrithviWeatherNet + GBM Ensemble specifically for Lahore.

Lahore coordinates : lat=31.5204, lon=74.3587
Data source        : weather_dataset_2000_2026_4h.csv  (station_name == 'Lahore')
                     Fallback: weather_training_dataset_2010_2026.csv (lat ~= 31.5204)
"""

import os
import sys
import json
import time
import joblib
import numpy as np
import csv
from datetime import datetime

# ── paths ──────────────────────────────────────────────────────────────────────
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

PRITHVI_PATH = r"C:\Users\Hp\prithvi"
if os.path.exists(PRITHVI_PATH) and PRITHVI_PATH not in sys.path:
    sys.path.insert(0, PRITHVI_PATH)

# ── imports that require the project ──────────────────────────────────────────
import torch
import torch.nn as nn
from torch.utils.data import TensorDataset, DataLoader
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.ensemble import HistGradientBoostingRegressor

try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False

from prithvi_weather_model import (
    PrithviWeatherNet,
    extract_spatiotemporal_features,
    WEATHER_TARGETS,
)

# ── config ────────────────────────────────────────────────────────────────────
LAHORE_LAT = 31.5204
LAHORE_LON = 74.3587
LAHORE_STATION = "Lahore"

SOURCE_4H   = os.path.join(script_dir, "weather_dataset_2000_2026_4h.csv")
SOURCE_DAILY = os.path.join(script_dir, "weather_training_dataset_2010_2026.csv")

OUT_CSV      = os.path.join(script_dir, "lahore_weather_training_data.csv")
OUT_PT       = os.path.join(script_dir, "lahore_prithvi_weather_net.pt")
OUT_GBM      = os.path.join(script_dir, "lahore_weather_gbm_ensemble.pkl")
OUT_META     = os.path.join(script_dir, "lahore_model_metadata.json")


# ── helpers ───────────────────────────────────────────────────────────────────
def _filter_lahore_csv(src_path: str, out_path: str) -> int:
    """Read src CSV, keep only Lahore rows, write to out_path.  Returns row count."""
    with open(src_path, newline="", encoding="utf-8") as fin, \
         open(out_path, "w", newline="", encoding="utf-8") as fout:

        reader = csv.DictReader(fin)
        fieldnames = reader.fieldnames
        writer = csv.DictWriter(fout, fieldnames=fieldnames)
        writer.writeheader()

        count = 0
        for row in reader:
            # Match by station_name or by lat
            if "station_name" in row:
                if row["station_name"].strip().lower() == LAHORE_STATION.lower():
                    writer.writerow(row)
                    count += 1
            else:
                try:
                    if abs(float(row["lat"]) - LAHORE_LAT) < 0.01:
                        writer.writerow(row)
                        count += 1
                except (KeyError, ValueError):
                    pass
    return count


def prepare_lahore_dataset() -> str:
    """Locate source data, extract Lahore rows, return path to Lahore CSV."""

    # Prefer the richer 4-hour 2000-2026 dataset
    if os.path.exists(SOURCE_4H):
        print(f"[*] Filtering Lahore rows from: {os.path.basename(SOURCE_4H)}")
        n = _filter_lahore_csv(SOURCE_4H, OUT_CSV)
        print(f"[+] Extracted {n:,} Lahore records  →  {OUT_CSV}")
        if n == 0:
            raise RuntimeError("No Lahore rows found in weather_dataset_2000_2026_4h.csv")
        return OUT_CSV

    # Fallback to daily 2010-2026 dataset
    if os.path.exists(SOURCE_DAILY):
        print(f"[*] Filtering Lahore rows from: {os.path.basename(SOURCE_DAILY)}")
        n = _filter_lahore_csv(SOURCE_DAILY, OUT_CSV)
        print(f"[+] Extracted {n:,} Lahore records  →  {OUT_CSV}")
        if n == 0:
            raise RuntimeError("No Lahore rows found in weather_training_dataset_2010_2026.csv")
        return OUT_CSV

    raise FileNotFoundError(
        "Neither weather_dataset_2000_2026_4h.csv nor "
        "weather_training_dataset_2010_2026.csv found in project directory."
    )


def load_dataset(csv_path: str):
    """Load dataset from CSV using pandas or pure csv fallback."""
    if HAS_PANDAS:
        df = pd.read_csv(csv_path)
        return df
    # Pure-csv fallback: build a dict of columns
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    if not rows:
        raise RuntimeError("Empty CSV file.")
    keys = rows[0].keys()
    data = {k: [] for k in keys}
    for row in rows:
        for k in keys:
            data[k].append(row[k])
    import pandas as _pd
    return _pd.DataFrame(data)


# ── main training function ────────────────────────────────────────────────────
def train(epochs: int = 30, batch_size: int = 64, lr: float = 1e-3):
    print("\n" + "=" * 70)
    print("  LAHORE WEATHER AI — Prithvi-Informed Training Pipeline")
    print(f"  Location : Lahore  (lat={LAHORE_LAT}, lon={LAHORE_LON})")
    print("=" * 70)

    # 1. Prepare Lahore dataset
    csv_path = prepare_lahore_dataset()

    # 2. Load
    if HAS_PANDAS:
        import pandas as pd
        df = pd.read_csv(csv_path)
    else:
        df = load_dataset(csv_path)

    print(f"[+] Loaded {len(df):,} Lahore records")
    print(f"    Columns : {list(df.columns)}")

    # Verify targets
    missing = [t for t in WEATHER_TARGETS if t not in df.columns]
    if missing:
        raise KeyError(f"Missing target columns: {missing}")

    # Drop rows with NaN targets
    before = len(df)
    df = df.dropna(subset=WEATHER_TARGETS)
    if len(df) < before:
        print(f"[!] Dropped {before - len(df):,} rows with NaN targets")

    # 3. Feature extraction
    X, feature_names = extract_spatiotemporal_features(
        df["lat"], df["lon"], df["validdate"]
    )
    Y = df[WEATHER_TARGETS].values.astype(np.float32)
    print(f"[+] Features ({X.shape[1]}): {', '.join(feature_names)}")
    print(f"[+] Targets  ({Y.shape[1]}): {', '.join(WEATHER_TARGETS)}")

    # 4. Train / Test split
    X_train, X_test, Y_train, Y_test = train_test_split(
        X, Y, test_size=0.2, random_state=42, shuffle=True
    )
    print(f"[+] Train : {len(X_train):,}  |  Test : {len(X_test):,}")

    # ── Stage 1: PrithviWeatherNet ────────────────────────────────────────────
    print(f"\n>>> [Stage 1/2] Training PrithviWeatherNet (PyTorch Deep Learning)...")
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"    Device : {device}")

    train_ds = TensorDataset(torch.from_numpy(X_train), torch.from_numpy(Y_train))
    test_ds  = TensorDataset(torch.from_numpy(X_test),  torch.from_numpy(Y_test))
    train_dl = DataLoader(train_ds, batch_size=batch_size, shuffle=True)
    test_dl  = DataLoader(test_ds,  batch_size=batch_size)

    model = PrithviWeatherNet(embed_dim=64, hidden_dim=256, num_blocks=3).to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-4)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs)
    criterion = nn.SmoothL1Loss()

    t0 = time.time()
    for epoch in range(1, epochs + 1):
        model.train()
        train_loss = 0.0
        for bx, by in train_dl:
            bx, by = bx.to(device), by.to(device)
            optimizer.zero_grad()
            loss = criterion(model(bx), by)
            loss.backward()
            nn.utils.clip_grad_norm_(model.parameters(), 2.0)
            optimizer.step()
            train_loss += loss.item() * len(bx)
        train_loss /= len(train_ds)
        scheduler.step()

        if epoch % 5 == 0 or epoch == epochs:
            model.eval()
            val_loss = 0.0
            with torch.no_grad():
                for bx, by in test_dl:
                    bx, by = bx.to(device), by.to(device)
                    val_loss += criterion(model(bx), by).item() * len(bx)
            val_loss /= len(test_ds)
            print(f"    Epoch {epoch:3d}/{epochs} — Train Loss: {train_loss:.4f} | Val Loss: {val_loss:.4f}")

    print(f"    Finished in {time.time() - t0:.1f}s")

    model.eval()
    with torch.no_grad():
        nn_preds = model(torch.from_numpy(X_test).to(device)).cpu().numpy()

    # ── Stage 2: GBM Ensemble ────────────────────────────────────────────────
    print(f"\n>>> [Stage 2/2] Training WeatherGBMEnsemble (Gradient Boosted Regressors)...")
    gbm_models = {}
    gbm_preds  = np.zeros_like(Y_test)

    for i, name in enumerate(WEATHER_TARGETS):
        print(f"    Training regressor for {name}...", end="", flush=True)
        reg = HistGradientBoostingRegressor(
            max_iter=200,
            learning_rate=0.07,
            max_leaf_nodes=63,
            random_state=42,
        )
        reg.fit(X_train, Y_train[:, i])
        gbm_models[name] = reg
        gbm_preds[:, i] = reg.predict(X_test)
        print(" done")

    # ── Ensemble + Metrics ────────────────────────────────────────────────────
    ens_preds = 0.5 * nn_preds + 0.5 * gbm_preds

    target_display = {
        "t_2m:C":                  "Temperature (°C)",
        "precip_1h:mm":            "Precipitation (mm)",
        "relative_humidity_2m:p":  "Relative Humidity (%)",
        "wind_speed_10m:ms":       "Wind Speed (m/s)",
        "msl_pressure:hPa":        "Sea Level Pressure (hPa)",
    }

    print("\n" + "=" * 70)
    print(f"{'WEATHER PARAMETER':<26} | {'MAE':<8} | {'RMSE':<8} | {'R² SCORE':<8}")
    print("-" * 70)

    metrics = {}
    for i, name in enumerate(WEATHER_TARGETS):
        mae  = mean_absolute_error(Y_test[:, i], ens_preds[:, i])
        rmse = np.sqrt(mean_squared_error(Y_test[:, i], ens_preds[:, i]))
        r2   = r2_score(Y_test[:, i], ens_preds[:, i])
        disp = target_display[name]
        print(f"{disp:<26} | {mae:<8.3f} | {rmse:<8.3f} | {r2:<8.3f}")
        metrics[name] = {"mae": float(mae), "rmse": float(rmse), "r2": float(r2)}

    print("=" * 70)

    # ── Save artifacts ────────────────────────────────────────────────────────
    torch.save({
        "state_dict":   model.state_dict(),
        "embed_dim":    64,
        "hidden_dim":   256,
        "num_blocks":   3,
        "feature_names": feature_names,
        "targets":      WEATHER_TARGETS,
        "station":      LAHORE_STATION,
        "lat":          LAHORE_LAT,
        "lon":          LAHORE_LON,
    }, OUT_PT)
    print(f"\n[+] Saved PyTorch model  →  {OUT_PT}")

    joblib.dump(gbm_models, OUT_GBM)
    print(f"[+] Saved GBM ensemble   →  {OUT_GBM}")

    meta = {
        "training_timestamp": datetime.now().isoformat(),
        "station":            LAHORE_STATION,
        "lat":                LAHORE_LAT,
        "lon":                LAHORE_LON,
        "dataset_used":       os.path.basename(csv_path),
        "total_samples":      len(df),
        "targets":            WEATHER_TARGETS,
        "feature_names":      feature_names,
        "metrics":            metrics,
    }
    with open(OUT_META, "w") as f:
        json.dump(meta, f, indent=2)
    print(f"[+] Saved metadata       →  {OUT_META}")
    print(f"\n[✓] Lahore model training complete!\n")
    return metrics


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Train Lahore-Specific Prithvi Weather AI")
    parser.add_argument("--epochs",     type=int,   default=30,  help="Training epochs (default: 30)")
    parser.add_argument("--batch-size", type=int,   default=64,  help="Batch size (default: 64)")
    parser.add_argument("--lr",         type=float, default=1e-3, help="Learning rate (default: 0.001)")
    args = parser.parse_args()

    train(epochs=args.epochs, batch_size=args.batch_size, lr=args.lr)
