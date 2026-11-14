"""
Training Pipeline for Prithvi-Informed Weather AI
=================================================
Trains both:
1. PyTorch Deep Neural Network (PrithviWeatherNet) using Prithvi harmonic spatial/temporal encoders
2. Gradient Boosted Weather Regressors (WeatherGBMEnsemble)
Evaluates on a holdout test set and exports ready-to-use inference checkpoints.
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

# Add local path and prithvi path
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.append(script_dir)

from prithvi_weather_model import (
    PrithviWeatherNet,
    extract_spatiotemporal_features,
    WEATHER_TARGETS
)

def train(data_path=None, epochs=25, batch_size=64, lr=1e-3):
    if data_path is None:
        file_2010_2026 = os.path.join(script_dir, "weather_training_dataset_2010_2026.csv")
        file_default = os.path.join(script_dir, "weather_training_dataset.csv")
        if os.path.exists(file_2010_2026):
            data_path = file_2010_2026
        elif os.path.exists(file_default):
            data_path = file_default
        else:
            # Look for any islamabad_weather_*.csv
            csv_candidates = [f for f in os.listdir(script_dir) if f.startswith("islamabad_weather_") and f.endswith(".csv")]
            if csv_candidates:
                data_path = os.path.join(script_dir, sorted(csv_candidates)[-1])
            else:
                raise FileNotFoundError("No weather CSV found.")

    print(f"\n" + "="*70)
    print(f"[*] TRAINING PRITHVI-INFORMED WEATHER PREDICTION AI")
    print(f"[*] Dataset: {os.path.basename(data_path)}")
    print(f"="*70)

    # 1. Load data
    df = pd.read_csv(data_path)
    print(f"[+] Loaded {len(df):,} records with columns: {list(df.columns)}")

    # Verify target columns
    for t in WEATHER_TARGETS:
        if t not in df.columns:
            raise KeyError(f"Target column '{t}' missing from dataset.")

    # 2. Extract features & targets
    X, feature_names = extract_spatiotemporal_features(df["lat"], df["lon"], df["validdate"])
    Y = df[WEATHER_TARGETS].values.astype(np.float32)

    print(f"[+] Extracted {X.shape[1]} spatio-temporal features: {', '.join(feature_names)}")

    # 3. Train / Test Split
    X_train, X_test, Y_train, Y_test = train_test_split(
        X, Y, test_size=0.2, random_state=42, shuffle=True
    )
    print(f"[+] Train set: {len(X_train):,} samples | Test set: {len(X_test):,} samples")

    # -------------------------------------------------------------
    # 4. Train Model 1: PrithviWeatherNet (PyTorch Deep Learning)
    # -------------------------------------------------------------
    print(f"\n>>> [Stage 1/2] Training PrithviWeatherNet (PyTorch Neural Network)...")
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"    Compute device: {device}")

    train_dataset = TensorDataset(torch.from_numpy(X_train), torch.from_numpy(Y_train))
    test_dataset = TensorDataset(torch.from_numpy(X_test), torch.from_numpy(Y_test))

    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)

    model = PrithviWeatherNet(embed_dim=64, hidden_dim=256, num_blocks=3).to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-4)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs)
    criterion = nn.SmoothL1Loss()  # Huber loss robust to extreme weather

    start_time = time.time()
    for epoch in range(1, epochs + 1):
        model.train()
        train_loss = 0.0
        for batch_x, batch_y in train_loader:
            batch_x, batch_y = batch_x.to(device), batch_y.to(device)
            optimizer.zero_grad()
            preds = model(batch_x)
            loss = criterion(preds, batch_y)
            loss.backward()
            nn.utils.clip_grad_norm_(model.parameters(), max_norm=2.0)
            optimizer.step()
            train_loss += loss.item() * len(batch_x)

        train_loss /= len(train_dataset)
        scheduler.step()

        if epoch % 5 == 0 or epoch == epochs:
            model.eval()
            val_loss = 0.0
            with torch.no_grad():
                for batch_x, batch_y in test_loader:
                    batch_x, batch_y = batch_x.to(device), batch_y.to(device)
                    preds = model(batch_x)
                    val_loss += criterion(preds, batch_y).item() * len(batch_x)
            val_loss /= len(test_dataset)
            print(f"    Epoch {epoch:2d}/{epochs} - Train Loss: {train_loss:.4f} | Val Loss: {val_loss:.4f}")

    print(f"    PrithviWeatherNet training completed in {time.time() - start_time:.1f}s")

    # Evaluate PyTorch Model
    model.eval()
    with torch.no_grad():
        nn_preds = model(torch.from_numpy(X_test).to(device)).cpu().numpy()

    # -------------------------------------------------------------
    # 5. Train Model 2: WeatherGBMEnsemble (Gradient Boosted Trees)
    # -------------------------------------------------------------
    print(f"\n>>> [Stage 2/2] Training WeatherGBMEnsemble (Gradient Boosted Regressors)...")
    gbm_models = {}
    gbm_preds = np.zeros_like(Y_test)

    for i, target_name in enumerate(WEATHER_TARGETS):
        print(f"    Training regressor for {target_name}...", end="", flush=True)
        reg = HistGradientBoostingRegressor(
            max_iter=150,
            learning_rate=0.08,
            max_leaf_nodes=31,
            random_state=42
        )
        reg.fit(X_train, Y_train[:, i])
        gbm_models[target_name] = reg
        gbm_preds[:, i] = reg.predict(X_test)
        print(" done", flush=True)

    # -------------------------------------------------------------
    # 6. Ensemble Predictions & Evaluation Metrics
    # -------------------------------------------------------------
    ensemble_preds = 0.5 * nn_preds + 0.5 * gbm_preds

    print(f"\n" + "="*70)
    print(f"{'WEATHER PARAMETER':<26} | {'MAE':<8} | {'RMSE':<8} | {'R² SCORE':<8}")
    print(f"-"*70)

    target_display = {
        "t_2m:C": "Temperature (°C)",
        "precip_1h:mm": "Precipitation (mm)",
        "relative_humidity_2m:p": "Relative Humidity (%)",
        "wind_speed_10m:ms": "Wind Speed (m/s)",
        "msl_pressure:hPa": "Sea Level Pressure (hPa)"
    }

    metrics = {}
    for i, target_name in enumerate(WEATHER_TARGETS):
        mae = mean_absolute_error(Y_test[:, i], ensemble_preds[:, i])
        rmse = np.sqrt(mean_squared_error(Y_test[:, i], ensemble_preds[:, i]))
        r2 = r2_score(Y_test[:, i], ensemble_preds[:, i])
        disp = target_display[target_name]
        print(f"{disp:<26} | {mae:<8.2f} | {rmse:<8.2f} | {r2:<8.3f}")
        metrics[target_name] = {"mae": float(mae), "rmse": float(rmse), "r2": float(r2)}

    print(f"="*70)

    # -------------------------------------------------------------
    # 7. Save Models and Metadata
    # -------------------------------------------------------------
    pt_path = os.path.join(script_dir, "prithvi_weather_net.pt")
    torch.save({
        "state_dict": model.state_dict(),
        "embed_dim": 64,
        "hidden_dim": 256,
        "num_blocks": 3,
        "feature_names": feature_names,
        "targets": WEATHER_TARGETS
    }, pt_path)
    print(f"\n[+] Saved PyTorch Model: {pt_path}")

    gbm_path = os.path.join(script_dir, "weather_gbm_ensemble.pkl")
    joblib.dump(gbm_models, gbm_path)
    print(f"[+] Saved GBM Ensemble:  {gbm_path}")

    meta_path = os.path.join(script_dir, "weather_model_metadata.json")
    meta = {
        "training_timestamp": datetime.now().isoformat(),
        "dataset_used": os.path.basename(data_path),
        "total_samples": len(df),
        "targets": WEATHER_TARGETS,
        "feature_names": feature_names,
        "metrics": metrics
    }
    with open(meta_path, "w") as f:
        json.dump(meta, f, indent=2)
    print(f"[+] Saved Metadata:      {meta_path}")
    print(f"[+] Training completed successfully!\n")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Train Prithvi-Informed Weather AI")
    parser.add_argument("--data", type=str, default=None, help="Path to training CSV")
    parser.add_argument("--epochs", type=int, default=25, help="Number of PyTorch training epochs")
    parser.add_argument("--batch-size", type=int, default=64, help="Batch size")
    parser.add_argument("--lr", type=float, default=1e-3, help="Learning rate")
    args = parser.parse_args()

    train(data_path=args.data, epochs=args.epochs, batch_size=args.batch_size, lr=args.lr)
