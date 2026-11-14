# NASA Field Shift: Prithvi AI Spatio-Temporal Weather Forecaster
### NASA Space Apps Hackathon 2026

An AI-driven future weather forecasting system built on top of the **NASA-IBM Prithvi Foundation Model** architecture and historical **Meteomatics** weather observation data.

Given **any location** (latitude, longitude) and **any future target timestamp**, this system predicts 5 key meteorological variables:
1. **Temperature (°C & °F)** (`t_2m:C`)
2. **Precipitation (mm/h)** (`precip_1h:mm`)
3. **Relative Humidity (%)** (`relative_humidity_2m:p`)
4. **Wind Speed (m/s & km/h)** (`wind_speed_10m:ms`)
5. **Mean Sea Level Pressure (hPa)** (`msl_pressure:hPa`)
6. **Overall Weather Condition Summary** (e.g., Clear & Mild, Hot & Sunny, Cold & Clear, Passing Showers, etc.)

---

## 🏛️ System Architecture

```
           [ Latitude, Longitude ]            [ Future Timestamp (Date & Hour) ]
                      │                                      │
                      ▼                                      ▼
       ┌───────────────────────────────┐     ┌────────────────────────────────┐
       │   NASA-IBM Prithvi Location   │     │    NASA-IBM Prithvi Temporal   │
       │    Harmonic Sin/Cos Encoder   │     │     Harmonic Sin/Cos Encoder   │
       │      (prithvi_mae.py)         │     │       (prithvi_mae.py)         │
       └──────────────┬────────────────┘     └───────────────┬────────────────┘
                      │ (64-dim)                             │ (64-dim)
                      └──────────────────────┬───────────────┘
                                             │
                      ┌──────────────────────┴────────────────┐
                      │     Cyclic Diurnal & Seasonal Head    │
                      │  (Sin/Cos Hour, Day of Year, Month)   │ (9-dim)
                      └──────────────────────┬────────────────┘
                                             │ (137-dim input)
                                             ▼
                      ┌───────────────────────────────────────┐
                      │    Deep Residual Neural Network       │
                      │    (LayerNorm + GELU + ResBlocks)     │
                      └──────────────────────┬────────────────┘
                                             │
             ┌───────────────────────────────┴───────────────────────────────┐
             ▼                                                               ▼
  ┌──────────────────────┐                                        ┌──────────────────────┐
  │   PyTorch Model      │                                        │   GBM Ensemble       │
  │  (prithvi_weather_   │                                        │  (HistGradient-      │
  │     net.pt)          │                                        │   Boosting)          │
  └──────────┬───────────┘                                        └──────────┬───────────┘
             │                                                               │
             └───────────────────────────────┬───────────────────────────────┘
                                             ▼
                           ┌───────────────────────────────────┐
                           │    Consensus Multi-Task Output    │
                           │   Temp, Rain, Humidity, Wind, P   │
                           └───────────────────────────────────┘
```

---

## 📂 Project Structure

```
NASA-SpaceApps-Hackathon-2026/
│
├── NASA Field Shift.py           # Original script to query Meteomatics API (fixed saving path)
├── download_weather_dataset.py  # Multi-year, multi-station dataset builder
├── prithvi_weather_model.py     # Prithvi-informed Neural Network architecture & feature extractor
├── train_weather_ai.py          # Complete training pipeline (trains PyTorch & GBM models)
├── predict_weather.py           # CLI and Python API for future weather forecasting
├── test_weather_predictions.py  # Unit & physical sanity tests
├── weather_training_dataset.csv # Downloaded 11,684 records (2022-2024 at 6h intervals)
├── prithvi_weather_net.pt       # Trained PyTorch neural network checkpoint
├── weather_gbm_ensemble.pkl     # Trained Gradient Boosted regressor models
└── weather_model_metadata.json  # Model configuration, features, and evaluation metrics
```

---

## 🚀 Quickstart & Usage

### 1. Predict Future Weather via Command Line
Run `predict_weather.py` with latitude, longitude, and any future timestamp:

```bash
python predict_weather.py --lat 33.6844 --lon 73.0479 --time "2026-11-20 14:00:00"
```

**Output:**
```
============================================================
           PRITHVI AI FUTURE WEATHER FORECAST
============================================================
 Location:       Lat 33.6844, Lon 73.0479
 Target Time:    2026-11-20 14:00:00 UTC
 Condition:      >> Partly Cloudy <<
------------------------------------------------------------
 Temperature:        16.4 °C  (61.6 °F)
 Precipitation:      0.03 mm/h
 Relative Humidity:  69.5 %
 Wind Speed:         1.5 m/s  (5.5 km/h)
 Sea Level Pressure: 1017.8 hPa
------------------------------------------------------------
 Neural Network:  16.0°C | 71.4% | 1.5m/s | 1018.1hPa
 GBM Ensemble:    16.8°C | 67.6% | 1.6m/s | 1017.5hPa
============================================================
```

### 2. Interactive CLI Mode
Run without arguments to enter location and date interactively:
```bash
python predict_weather.py
```

### 3. Use in Python Scripts
```python
from predict_weather import predict_weather

result = predict_weather(
    lat=33.6844,
    lon=73.0479,
    target_time="2026-12-25 14:00:00"
)

print("Condition:", result["condition"])
print("Temperature:", result["forecast"]["temperature_c"], "°C")
print("Precipitation:", result["forecast"]["precipitation_mm"], "mm")
print("Humidity:", result["forecast"]["relative_humidity_pct"], "%")
print("Wind Speed:", result["forecast"]["wind_speed_ms"], "m/s")
print("Pressure:", result["forecast"]["pressure_hpa"], "hPa")
```

---

## 📊 Model Evaluation Performance

Evaluated on an independent holdout test set (2,337 samples):

| Weather Parameter | Mean Absolute Error (MAE) | Root Mean Squared Error (RMSE) | $R^2$ Score |
| :--- | :--- | :--- | :--- |
| **Temperature (°C)** | **1.01 °C** | **1.36 °C** | **0.979** |
| **Sea Level Pressure (hPa)** | **0.87 hPa** | **1.13 hPa** | **0.974** |
| **Relative Humidity (%)** | **5.90 %** | **8.07 %** | **0.851** |
| **Wind Speed (m/s)** | **0.72 m/s** | **1.02 m/s** | **0.364** |
| **Precipitation (mm/h)** | **0.15 mm** | **0.48 mm** | **0.105** |

---

## 🔄 Retraining the Model

To retrain the model with updated data or parameters:
```bash
python train_weather_ai.py
```
This will automatically extract spatio-temporal features, train both the PyTorch `PrithviWeatherNet` and `WeatherGBMEnsemble`, evaluate performance metrics, and save new model weights.

---

## 🧪 Running Tests

To verify physical consistency, seasonal transitions, and spatial variation:
```bash
python test_weather_predictions.py
```
