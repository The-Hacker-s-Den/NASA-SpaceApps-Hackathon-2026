"""
Soil + Weather AI Training Pipeline
=====================================
Trains PrithviSoilWeatherNet (PyTorch) + GBM Ensemble on the combined
soil-weather dataset covering Islamabad, Murree, and Lahore (2016-2026).

Usage:
    python train_soil_weather_ai.py
    python train_soil_weather_ai.py --epochs 40 --batch-size 128
    python train_soil_weather_ai.py --data path/to/custom.csv
"""

import os
import sys
import json
import time
import joblib
import numpy as np
import pandas as pd
from datetime import datetime

import torch
import torch.nn as nn
from torch.utils.data import TensorDataset, DataLoader
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.ensemble import HistGradientBoostingRegressor

script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

from prithvi_soil_weather_model import (
    PrithviSoilWeatherNet,
    extract_spatiotemporal_features,
    ALL_TARGETS,
    WEATHER_TARGETS,
    SOIL_TARGETS,
    AQ_TARGETS,
    TARGET_DISPLAY,
)

# ── Output paths ───────────────────────────────────────────────────────────────
OUT_PT   = os.path.join(script_dir, "soil_weather_net.pt")
OUT_GBM  = os.path.join(script_dir, "soil_weather_gbm_ensemble.pkl")
OUT_META = os.path.join(script_dir, "soil_weather_model_metadata.json")

# ── Default data source priority ───────────────────────────────────────────────
PREFERRED_CSV = os.path.join(script_dir, "soil_weather_dataset_ISL_MUR_LHR.csv")
FALLBACK_CSV  = os.path.join(script_dir, "weather_dataset_2000_2026_4h.csv")


def _resolve_dataset(data_path=None):
    """Find the best available dataset with soil columns."""
    if data_path and os.path.exists(data_path):
        return data_path
    if os.path.exists(PREFERRED_CSV):
        return PREFERRED_CSV
    # Fall back to 4h weather dataset (no soil columns — partial training)
    if os.path.exists(FALLBACK_CSV):
        print("[!] Soil dataset not found. Falling back to weather-only dataset.")
        print("    Run download_soil_weather_dataset.py first for full soil training.")
        return FALLBACK_CSV
    raise FileNotFoundError(
        "No suitable dataset found. Run download_soil_weather_dataset.py first."
    )


def _load_and_validate(csv_path):
    """Load CSV, detect available targets, drop NaN rows."""
    df = pd.read_csv(csv_path)
    print(f"[+] Loaded {len(df):,} rows from {os.path.basename(csv_path)}")
    print(f"    Columns: {list(df.columns)}")

    if "station_name" in df.columns:
        print(f"    Stations: {df['station_name'].value_counts().to_dict()}")

    # Only keep targets that exist in this dataset
    available = [t for t in ALL_TARGETS if t in df.columns]
    missing   = [t for t in ALL_TARGETS if t not in df.columns]

    if missing:
        print(f"\n[!] Missing targets (will be skipped): {missing}")
        print(f"    Run download_soil_weather_dataset.py to get full soil data.\n")

    if not available:
        raise KeyError("No recognizable target columns found in dataset.")

    # Drop rows missing any available target
    before = len(df)
    df = df.dropna(subset=available)
    if len(df) < before:
        print(f"[!] Dropped {before - len(df):,} rows with NaN targets. "
              f"Remaining: {len(df):,}")

    return df, available


def train(data_path=None, epochs=35, batch_size=64, lr=1e-3):
    print("\n" + "=" * 70)
    print("  PRITHVI WEATHER + SOIL + AIR QUALITY AI — Training Pipeline")
    print("  Stations : Islamabad · Murree · Lahore")
    print("  Targets  : 5 Weather + 10 Soil + 1 Air Quality = 16 total outputs")
    print("=" * 70)

    # 1. Resolve and load dataset
    csv_path = _resolve_dataset(data_path)
    df, active_targets = _load_and_validate(csv_path)

    # 2. Feature extraction
    X, feature_names = extract_spatiotemporal_features(
        df["lat"], df["lon"], df["validdate"]
    )
    Y = df[active_targets].values.astype(np.float32)

    print(f"\n[+] Features ({X.shape[1]}): {', '.join(feature_names)}")
    print(f"[+] Active targets ({len(active_targets)}): {', '.join(active_targets)}")

    # 3. Train / test split
    X_train, X_test, Y_train, Y_test = train_test_split(
        X, Y, test_size=0.2, random_state=42, shuffle=True
    )
    print(f"[+] Train : {len(X_train):,}  |  Test : {len(X_test):,}")

    # ── Stage 1 : PrithviSoilWeatherNet ───────────────────────────────────────
    print(f"\n>>> [Stage 1/2] Training PrithviSoilWeatherNet (PyTorch Deep Learning)...")
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"    Device  : {device}")
    print(f"    Outputs : {len(active_targets)}")

    n_targets = len(active_targets)

    # Build model — adjust output heads if targets < 15 (partial dataset)
    model = PrithviSoilWeatherNet(
        embed_dim=64, hidden_dim=384, num_blocks=4
    ).to(device)

    # If dataset is partial, we need a lightweight output projection
    # We detect mismatch at forward by wrapping
    full_target_count = len(ALL_TARGETS)
    if n_targets < full_target_count:
        # Wrap: project last layer to n_targets only
        # We replace by patching forward output slicing
        model._active_target_count = n_targets
    else:
        model._active_target_count = full_target_count

    # Custom forward for partial target datasets
    original_forward = model.forward

    def _partial_forward(x):
        out = original_forward(x)
        return out[:, :n_targets]

    if n_targets < full_target_count:
        model.forward = _partial_forward

    train_ds = TensorDataset(torch.from_numpy(X_train), torch.from_numpy(Y_train))
    test_ds  = TensorDataset(torch.from_numpy(X_test),  torch.from_numpy(Y_test))
    train_dl = DataLoader(train_ds, batch_size=batch_size, shuffle=True,  num_workers=0)
    test_dl  = DataLoader(test_ds,  batch_size=batch_size, shuffle=False, num_workers=0)

    optimizer  = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-4)
    scheduler  = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs)
    criterion  = nn.SmoothL1Loss()

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
            elapsed = time.time() - t0
            print(f"    Epoch {epoch:3d}/{epochs} — "
                  f"Train: {train_loss:.4f} | Val: {val_loss:.4f} | "
                  f"Time: {elapsed:.0f}s")

    print(f"    PrithviSoilWeatherNet trained in {time.time() - t0:.1f}s")

    model.eval()
    with torch.no_grad():
        nn_preds = model(torch.from_numpy(X_test).to(device)).cpu().numpy()

    # ── Stage 2 : GBM Ensemble ─────────────────────────────────────────────────
    print(f"\n>>> [Stage 2/2] Training GBM Ensemble ({len(active_targets)} regressors)...")
    gbm_models = {}
    gbm_preds  = np.zeros((len(X_test), n_targets), dtype=np.float32)

    for i, name in enumerate(active_targets):
        print(f"    [{i+1:2d}/{n_targets}] {name[:40]:<40}", end="", flush=True)
        reg = HistGradientBoostingRegressor(
            max_iter=200,
            learning_rate=0.07,
            max_leaf_nodes=63,
            random_state=42,
        )
        reg.fit(X_train, Y_train[:, i])
        gbm_models[name] = reg
        gbm_preds[:, i]  = reg.predict(X_test)
        print(" ✓")

    # ── Ensemble + Metrics ─────────────────────────────────────────────────────
    ens_preds = 0.5 * nn_preds + 0.5 * gbm_preds

    print(f"\n{'='*72}")
    print(f"{'PARAMETER':<32} | {'MAE':>7} | {'RMSE':>7} | {'R²':>7} | STATUS")
    print(f"{'-'*72}")

    metrics = {}
    for i, name in enumerate(active_targets):
        mae  = mean_absolute_error(Y_test[:, i], ens_preds[:, i])
        rmse = np.sqrt(mean_squared_error(Y_test[:, i], ens_preds[:, i]))
        r2   = r2_score(Y_test[:, i], ens_preds[:, i])
        status = "✅" if r2 >= 0.7 else ("⚠️" if r2 >= 0.3 else "❌")
        disp = TARGET_DISPLAY.get(name, name)[:31]
        print(f"{disp:<32} | {mae:>7.3f} | {rmse:>7.3f} | {r2:>7.3f} | {status}")
        metrics[name] = {"mae": float(mae), "rmse": float(rmse), "r2": float(r2)}

    print(f"{'='*72}")

    # ── Save artifacts ─────────────────────────────────────────────────────────
    # Restore original forward before saving
    if n_targets < full_target_count:
        model.forward = original_forward

    torch.save({
        "state_dict":     model.state_dict(),
        "embed_dim":      64,
        "hidden_dim":     384,
        "num_blocks":     4,
        "feature_names":  feature_names,
        "targets":        active_targets,
        "all_targets":    ALL_TARGETS,
    }, OUT_PT)
    print(f"\n[+] PyTorch model  → {OUT_PT}")

    joblib.dump(gbm_models, OUT_GBM)
    print(f"[+] GBM ensemble   → {OUT_GBM}")

    meta = {
        "training_timestamp": datetime.now().isoformat(),
        "dataset_used":       os.path.basename(csv_path),
        "total_samples":      len(df),
        "stations":           ["Islamabad", "Murree", "Lahore"],
        "weather_targets":    WEATHER_TARGETS,
        "soil_targets":       SOIL_TARGETS,
        "aq_targets":         AQ_TARGETS,
        "active_targets":     active_targets,
        "feature_names":      feature_names,
        "metrics":            metrics,
    }
    with open(OUT_META, "w") as f:
        json.dump(meta, f, indent=2)
    print(f"[+] Metadata       → {OUT_META}")
    print(f"\n[✓] Training complete — {len(active_targets)} targets trained!\n")
    return metrics


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Train Prithvi Soil+Weather AI")
    parser.add_argument("--data",       type=str,   default=None,  help="Path to training CSV")
    parser.add_argument("--epochs",     type=int,   default=35,    help="Training epochs (default: 35)")
    parser.add_argument("--batch-size", type=int,   default=64,    help="Batch size (default: 64)")
    parser.add_argument("--lr",         type=float, default=1e-3,  help="Learning rate (default: 0.001)")
    args = parser.parse_args()

    train(data_path=args.data, epochs=args.epochs, batch_size=args.batch_size, lr=args.lr)
