"""
Future Weather Predictor using Trained Prithvi-Informed AI
=========================================================
Predicts future weather for any given location (latitude, longitude)
and future target time (date and hour).

Usage Examples:
---------------
1. Interactive CLI:
   python predict_weather.py

2. Command-line flags:
   python predict_weather.py --lat 33.6844 --lon 73.0479 --time "2026-12-25 14:00:00"

3. Python Import:
   from predict_weather import predict_weather
   result = predict_weather(lat=33.6844, lon=73.0479, target_time="2026-12-25 14:00:00")
   print(result)
"""

import os
import sys
import argparse
import joblib
import numpy as np
import pandas as pd
import torch
from datetime import datetime

script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.append(script_dir)

from prithvi_weather_model import (
    PrithviWeatherNet,
    extract_spatiotemporal_features,
    WEATHER_TARGETS
)

# Global model cache for fast repeated inference
_CACHED_NN = None
_CACHED_GBM = None


def load_models():
    global _CACHED_NN, _CACHED_GBM
    if _CACHED_NN is not None and _CACHED_GBM is not None:
        return _CACHED_NN, _CACHED_GBM

    pt_path = os.path.join(script_dir, "prithvi_weather_net.pt")
    gbm_path = os.path.join(script_dir, "weather_gbm_ensemble.pkl")

    if not os.path.exists(pt_path) or not os.path.exists(gbm_path):
        raise FileNotFoundError(
            f"Trained model files not found in {script_dir}. "
            "Please run 'python train_weather_ai.py' first."
        )

    device = torch.device("cpu")
    checkpoint = torch.load(pt_path, map_location=device)

    model = PrithviWeatherNet(
        embed_dim=checkpoint.get("embed_dim", 64),
        hidden_dim=checkpoint.get("hidden_dim", 256),
        num_blocks=checkpoint.get("num_blocks", 3)
    )
    model.load_state_dict(checkpoint["state_dict"])
    model.eval()

    gbm_models = joblib.load(gbm_path)

    _CACHED_NN = model
    _CACHED_GBM = gbm_models
    return _CACHED_NN, _CACHED_GBM


def determine_weather_condition(temp, precip, humidity, wind):
    """Derives a human-readable weather description from physical parameters"""
    if precip >= 1.0:
        if temp < 1.0:
            return "Snow / Freezing Rain"
        elif precip > 5.0:
            return "Heavy Rain / Downpour"
        else:
            return "Light to Moderate Rain"
    elif precip > 0.1:
        return "Passing Showers / Drizzle"
    elif humidity > 85.0:
        return "Overcast & Humid"
    elif humidity > 65.0:
        return "Partly Cloudy"
    elif wind > 8.0:
        return "Breezy / Windy & Clear"
    elif temp > 35.0:
        return "Hot & Sunny"
    elif temp < 5.0:
        return "Cold & Clear"
    else:
        return "Clear & Mild"


def predict_weather(lat: float, lon: float, target_time: str or datetime, blend_weight: float = 0.5):
    """
    Predicts weather variables for a given latitude, longitude, and future datetime.

    Parameters:
    -----------
    lat : float
        Latitude in decimal degrees (e.g. 33.6844 for Islamabad)
    lon : float
        Longitude in decimal degrees (e.g. 73.0479)
    target_time : str or datetime
        Future timestamp, e.g. "2026-11-20 14:00:00"
    blend_weight : float (0.0 to 1.0)
        Weight for neural network prediction (1 - blend_weight for GBM)

    Returns:
    --------
    dict with forecast summary, parameters, and individual model outputs.
    """
    nn_model, gbm_models = load_models()

    dt_target = pd.to_datetime(target_time)

    # Extract spatio-temporal features
    X, feat_names = extract_spatiotemporal_features([lat], [lon], [dt_target])

    # 1. Neural Network Prediction
    with torch.no_grad():
        x_tensor = torch.from_numpy(X).float()
        nn_out = nn_model(x_tensor).cpu().numpy()[0]

    # 2. GBM Ensemble Prediction
    gbm_out = np.zeros(len(WEATHER_TARGETS), dtype=np.float32)
    for i, t in enumerate(WEATHER_TARGETS):
        gbm_out[i] = gbm_models[t].predict(X)[0]

    # 3. Consensus Blend
    consensus = blend_weight * nn_out + (1.0 - blend_weight) * gbm_out

    # Clamp physically bounded outputs
    temp = float(consensus[0])
    precip = float(max(0.0, consensus[1]))
    humidity = float(np.clip(consensus[2], 0.0, 100.0))
    wind = float(max(0.0, consensus[3]))
    pressure = float(consensus[4])

    condition = determine_weather_condition(temp, precip, humidity, wind)

    return {
        "location": {"latitude": lat, "longitude": lon},
        "target_time": dt_target.strftime("%Y-%m-%d %H:%M:%S UTC"),
        "condition": condition,
        "forecast": {
            "temperature_c": round(temp, 1),
            "temperature_f": round(temp * 9.0 / 5.0 + 32.0, 1),
            "precipitation_mm": round(precip, 2),
            "relative_humidity_pct": round(humidity, 1),
            "wind_speed_ms": round(wind, 1),
            "wind_speed_kmh": round(wind * 3.6, 1),
            "pressure_hpa": round(pressure, 1)
        },
        "model_components": {
            "prithvi_nn": {
                "temp": round(float(nn_out[0]), 1),
                "precip": round(float(nn_out[1]), 2),
                "humidity": round(float(nn_out[2]), 1),
                "wind": round(float(nn_out[3]), 1),
                "pressure": round(float(nn_out[4]), 1)
            },
            "gbm_ensemble": {
                "temp": round(float(gbm_out[0]), 1),
                "precip": round(float(gbm_out[1]), 2),
                "humidity": round(float(gbm_out[2]), 1),
                "wind": round(float(gbm_out[3]), 1),
                "pressure": round(float(gbm_out[4]), 1)
            }
        }
    }


def print_weather_card(res):
    loc = res["location"]
    fc = res["forecast"]
    print("\n" + "="*60)
    print("           PRITHVI AI FUTURE WEATHER FORECAST")
    print("="*60)
    print(f" Location:       Lat {loc['latitude']:.4f}, Lon {loc['longitude']:.4f}")
    print(f" Target Time:    {res['target_time']}")
    print(f" Condition:      >> {res['condition']} <<")
    print("-" * 60)
    print(f" Temperature:        {fc['temperature_c']} °C  ({fc['temperature_f']} °F)")
    print(f" Precipitation:      {fc['precipitation_mm']} mm/h")
    print(f" Relative Humidity:  {fc['relative_humidity_pct']} %")
    print(f" Wind Speed:         {fc['wind_speed_ms']} m/s  ({fc['wind_speed_kmh']} km/h)")
    print(f" Sea Level Pressure: {fc['pressure_hpa']} hPa")
    print("-" * 60)
    nn_comp = res["model_components"]["prithvi_nn"]
    gbm_comp = res["model_components"]["gbm_ensemble"]
    print(f" Neural Network:  {nn_comp['temp']}°C | {nn_comp['humidity']}% | {nn_comp['wind']}m/s | {nn_comp['pressure']}hPa")
    print(f" GBM Ensemble:    {gbm_comp['temp']}°C | {gbm_comp['humidity']}% | {gbm_comp['wind']}m/s | {gbm_comp['pressure']}hPa")
    print("="*60 + "\n")


def main():
    parser = argparse.ArgumentParser(description="Predict future weather using Prithvi-informed AI.")
    parser.add_argument("--lat", type=float, default=None, help="Latitude (e.g. 33.6844 for Islamabad)")
    parser.add_argument("--lon", type=float, default=None, help="Longitude (e.g. 73.0479)")
    parser.add_argument("--time", type=str, default=None, help="Future datetime (e.g. '2026-11-20 14:00:00')")
    args = parser.parse_args()

    if args.lat is not None and args.lon is not None and args.time is not None:
        lat = args.lat
        lon = args.lon
        target_time = args.time
    else:
        print("\n--- PRITHVI WEATHER PREDICTION (INTERACTIVE MODE) ---")
        lat_in = input("Enter Latitude  [default: 33.6844 (Islamabad)]: ").strip()
        lat = float(lat_in) if lat_in else 33.6844

        lon_in = input("Enter Longitude [default: 73.0479]: ").strip()
        lon = float(lon_in) if lon_in else 73.0479

        time_in = input("Enter Future Date & Time (YYYY-MM-DD HH:MM) [default: 2026-11-20 14:00]: ").strip()
        target_time = time_in if time_in else "2026-11-20 14:00:00"

    res = predict_weather(lat, lon, target_time)
    print_weather_card(res)


if __name__ == "__main__":
    main()
