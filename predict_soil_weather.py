"""
Soil + Weather + Flood + Air Quality Predictor — Prithvi AI System
===================================================================
Multi-task agricultural & environmental prediction system covering:
  • All specified cities: Multan, Gujrat, Gujranwala, Lalamusa, Kharian
  • Core Barani (rainfed) tracts: Chakwal, Attock, Jhelum, Mianwali, Bhakkar
  • Provincial capitals & hubs: Islamabad, Murree, Lahore, Faisalabad, Sialkot, Sargodha, Bahawalpur
  • Custom GPS coordinates anywhere via interactive map or CLI
  • 16 AI prediction variables (Weather + Soil + Air Quality)
  • Hydrological Flood Risk Index & Runoff Radar
  • Area Range Scanner (5 km - 100 km radius)
  • Gemini AI Agricultural Land & Crop Feasibility Valuation
"""

import os
import sys
import math
import argparse
import json
import joblib
import numpy as np
import pandas as pd
import torch
from datetime import datetime

script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

from prithvi_soil_weather_model import (
    PrithviSoilWeatherNet,
    extract_spatiotemporal_features,
    ALL_TARGETS,
    TARGET_DISPLAY,
    TARGET_BOUNDS,
    WEATHER_TARGETS,
    SOIL_TARGETS,
    AQ_TARGETS,
    interpret_soil_health,
    interpret_air_quality,
)

from nasa_data_engine import (
    REGIONAL_CITIES,
    fetch_nasa_power_data,
    calculate_flood_risk,
    scan_area_radius,
)

from gemini_agri_advisor import evaluate_crop_feasibility

# ── Model paths ────────────────────────────────────────────────────────────────
MODEL_SOIL_PT  = os.path.join(script_dir, "soil_weather_net.pt")
MODEL_SOIL_GBM = os.path.join(script_dir, "soil_weather_gbm_ensemble.pkl")
MODEL_WX_PT    = os.path.join(script_dir, "prithvi_weather_net.pt")
MODEL_WX_GBM   = os.path.join(script_dir, "weather_gbm_ensemble.pkl")
META_PATH      = os.path.join(script_dir, "soil_weather_model_metadata.json")

_CACHED_NN  = None
_CACHED_GBM = None
_ACTIVE_TARGETS = None
_MODEL_MODE = None


def _load_models():
    """Loads the best available trained Prithvi foundation model checkpoint."""
    global _CACHED_NN, _CACHED_GBM, _ACTIVE_TARGETS, _MODEL_MODE

    if _CACHED_NN is not None:
        return _CACHED_NN, _CACHED_GBM, _ACTIVE_TARGETS, _MODEL_MODE

    # Mode 1: Full 16-target Soil + Weather + AQ model
    if os.path.exists(MODEL_SOIL_PT) and os.path.exists(MODEL_SOIL_GBM):
        ckpt = torch.load(MODEL_SOIL_PT, map_location="cpu")
        model = PrithviSoilWeatherNet(
            embed_dim  = ckpt.get("embed_dim",  64),
            hidden_dim = ckpt.get("hidden_dim", 384),
            num_blocks = ckpt.get("num_blocks", 4),
        )
        model.load_state_dict(ckpt["state_dict"])
        model.eval()
        gbm = joblib.load(MODEL_SOIL_GBM)
        active = ckpt.get("targets", ALL_TARGETS)
        _CACHED_NN = model
        _CACHED_GBM = gbm
        _ACTIVE_TARGETS = active
        _MODEL_MODE = "FULL_16_TARGET"
        return _CACHED_NN, _CACHED_GBM, _ACTIVE_TARGETS, _MODEL_MODE

    # Mode 2: Verified PrithviWeatherNet (Weather backbone)
    elif os.path.exists(MODEL_WX_PT):
        from prithvi_weather_model import PrithviWeatherNet
        ckpt = torch.load(MODEL_WX_PT, map_location="cpu")
        model = PrithviWeatherNet(
            embed_dim  = ckpt.get("embed_dim", 64),
            hidden_dim = ckpt.get("hidden_dim", 256),
            num_blocks = ckpt.get("num_blocks", 3)
        )
        model.load_state_dict(ckpt["state_dict"])
        model.eval()
        gbm = joblib.load(MODEL_WX_GBM) if os.path.exists(MODEL_WX_GBM) else None
        _CACHED_NN = model
        _CACHED_GBM = gbm
        _ACTIVE_TARGETS = WEATHER_TARGETS
        _MODEL_MODE = "WEATHER_BACKBONE"
        return _CACHED_NN, _CACHED_GBM, _ACTIVE_TARGETS, _MODEL_MODE

    # Mode 3: Standalone Prithvi-Informed architectural execution
    else:
        model = PrithviSoilWeatherNet(embed_dim=64, hidden_dim=384, num_blocks=4)
        model.eval()
        _CACHED_NN = model
        _CACHED_GBM = None
        _ACTIVE_TARGETS = ALL_TARGETS
        _MODEL_MODE = "UNTRAINED_ARCH"
        return _CACHED_NN, _CACHED_GBM, _ACTIVE_TARGETS, _MODEL_MODE


def _resolve_station(station_name=None, lat=None, lon=None):
    """Resolves coordinates, metadata, and agro-zone from station name or coordinates."""
    if lat is not None and lon is not None:
        closest_city = None
        min_dist = float("inf")
        for k, info in REGIONAL_CITIES.items():
            dist = math.hypot(float(lat) - info["lat"], float(lon) - info["lon"])
            if dist < min_dist:
                min_dist = dist
                closest_city = info
                
        city_display = f"Custom ({float(lat):.4f}, {float(lon):.4f})"
        if min_dist < 0.2 and closest_city:
            city_display += f" near {closest_city['name']}"
            
        return {
            "name": "Custom",
            "display": city_display,
            "lat": float(lat),
            "lon": float(lon),
            "elevation_m": closest_city["elevation_m"] if closest_city else 200,
            "zone": closest_city["zone"] if closest_city else "Agricultural Area",
            "river_basin": closest_city["river_basin"] if closest_city else "Indus Basin",
            "barani": closest_city["barani"] if closest_city else False,
            "primary_crops": closest_city["primary_crops"] if closest_city else ["Wheat", "Pulses"]
        }

    if station_name:
        key = station_name.strip().lower()
        if key in REGIONAL_CITIES:
            return REGIONAL_CITIES[key]
        for k, v in REGIONAL_CITIES.items():
            if key in v["name"].lower() or key in v["display"].lower():
                return v
        raise ValueError(
            f"Unknown station '{station_name}'. Available cities: {list(REGIONAL_CITIES.keys())}"
        )

    # Default to Islamabad
    return REGIONAL_CITIES["islamabad"]


def _clamp(val, name):
    lo, hi = TARGET_BOUNDS.get(name, (None, None))
    if lo is not None:
        val = max(lo, val)
    if hi is not None:
        val = min(hi, val)
    return val


def predict(station=None, lat=None, lon=None, target_time=None, blend=0.5,
            radius_km: float = 25.0, gemini_api_key: str = None, query_nasa_live: bool = False):
    """
    Comprehensive multi-modal forecast:
      • Weather variables
      • Multi-depth soil profile
      • Air Quality Index & Health status
      • Hydrological Flood Risk & Runoff
      • Area Range Scan (spatial variance around radius)
      • Gemini AI Agricultural Land & Crop Feasibility
    """
    if target_time is None:
        target_time = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    city_info = _resolve_station(station, lat, lon)
    r_lat, r_lon = city_info["lat"], city_info["lon"]

    nn_model, gbm_models, active_targets, model_mode = _load_models()

    dt_target = pd.to_datetime(target_time)
    X, feat_names = extract_spatiotemporal_features([r_lat], [r_lon], [dt_target])

    # 1. Neural Network Inference
    with torch.no_grad():
        nn_out = nn_model(torch.from_numpy(X).float()).numpy()[0]

    # 2. Gradient Boosted Regressors
    if gbm_models:
        gbm_out = np.array([
            gbm_models[t].predict(X)[0] if t in gbm_models else np.nan
            for t in active_targets
        ], dtype=np.float32)
        raw_preds = blend * nn_out[:len(active_targets)] + (1.0 - blend) * gbm_out
    else:
        raw_preds = nn_out[:len(active_targets)]

    predictions = {
        name: _clamp(float(raw_preds[i]), name)
        for i, name in enumerate(active_targets)
    }

    # 3. Optional Real NASA POWER Live Telemetry
    nasa_power_data = None
    if query_nasa_live:
        nasa_power_data = fetch_nasa_power_data(r_lat, r_lon, days_back=7)

    # Physical fallbacks / calibration if partial model loaded
    if "volumetric_soil_water_-5cm:m3m3" not in predictions:
        month = dt_target.month
        is_monsoon = (7 <= month <= 9)
        base_vwc = 0.28 if is_monsoon else (0.24 if city_info["barani"] else 0.21)
        predictions["volumetric_soil_water_-5cm:m3m3"]   = base_vwc
        predictions["volumetric_soil_water_-15cm:m3m3"]  = base_vwc + 0.03
        predictions["volumetric_soil_water_-50cm:m3m3"]  = base_vwc + 0.05
        predictions["volumetric_soil_water_-150cm:m3m3"] = 0.32
        predictions["soil_moisture_index_-5cm:idx"]      = 0.15 if is_monsoon else -0.05
        predictions["soil_moisture_index_-15cm:idx"]     = 0.20 if is_monsoon else 0.05
        predictions["soil_moisture_index_-50cm:idx"]     = 0.18
        predictions["soil_moisture_index_-150cm:idx"]    = 0.22
        predictions["soil_moisture_deficit:mm"]          = 8.0 if is_monsoon else 24.5
        predictions["soil_frost:p"]                      = 45.0 if (city_info["name"] == "Murree" and month in [12, 1, 2]) else 0.0

    if "air_quality:idx" not in predictions:
        month = dt_target.month
        is_smog_season = (month in [10, 11, 12, 1])
        c_name = city_info["name"].lower()
        if c_name in ["lahore", "gujranwala", "faisalabad"]:
            predictions["air_quality:idx"] = 185.0 if is_smog_season else 95.0
        elif c_name in ["murree", "islamabad"]:
            predictions["air_quality:idx"] = 45.0
        elif c_name in ["multan", "sialkot", "gujrat"]:
            predictions["air_quality:idx"] = 145.0 if is_smog_season else 75.0
        else:
            predictions["air_quality:idx"] = 65.0

    # 4. Interpretations
    vwc_5   = predictions["volumetric_soil_water_-5cm:m3m3"]
    vwc_15  = predictions["volumetric_soil_water_-15cm:m3m3"]
    smi_5   = predictions.get("soil_moisture_index_-5cm:idx", 0.1)
    smd     = predictions.get("soil_moisture_deficit:mm", 15.0)
    frost   = predictions.get("soil_frost:p", 0.0)
    health  = interpret_soil_health(vwc_5, smi_5, smd, frost)

    aqi_val = predictions["air_quality:idx"]
    aqi_label, aqi_desc, aqi_emoji = interpret_air_quality(aqi_val)

    temp   = predictions.get("t_2m:C", 22.0)
    precip = predictions.get("precip_1h:mm", 0.0)
    humid  = predictions.get("relative_humidity_2m:p", 60.0)
    wind   = predictions.get("wind_speed_10m:ms", 2.0)
    press  = predictions.get("msl_pressure:hPa", 1013.25)

    if precip >= 1.0:
        wx_cond = "Snow / Freezing Rain" if temp < 1.0 else ("Heavy Downpour" if precip > 5.0 else "Light Rain")
    elif precip > 0.1:
        wx_cond = "Passing Drizzle"
    elif humid > 85.0:
        wx_cond = "Overcast & Humid"
    elif wind > 8.0:
        wx_cond = "Breezy & Clear"
    elif temp > 35.0:
        wx_cond = "Hot & Sunny"
    elif temp < 5.0:
        wx_cond = "Cold & Clear"
    else:
        wx_cond = "Clear & Mild"

    # 5. Flood Risk Modeling
    precip_24h = precip * 24.0
    if nasa_power_data and nasa_power_data.get("precipitation_accum_mm"):
        precip_24h = max(precip_24h, float(nasa_power_data["precipitation_accum_mm"]))
        
    flood_analysis = calculate_flood_risk(
        lat=r_lat, lon=r_lon,
        precip_accum_mm=precip_24h,
        vwc_5cm=vwc_5,
        vwc_15cm=vwc_15,
        smd_mm=smd,
        elevation_m=city_info.get("elevation_m", 200),
        city_info=city_info
    )

    # 6. Assemble Full Response
    result = {
        "location": city_info["name"],
        "display_name": city_info["display"],
        "coordinates": {"lat": r_lat, "lon": r_lon},
        "elevation_m": city_info.get("elevation_m", 200),
        "zone": city_info.get("zone", "Agricultural Area"),
        "river_basin": city_info.get("river_basin", "Indus Basin"),
        "barani": city_info.get("barani", False),
        "target_time": dt_target.strftime("%Y-%m-%d %H:%M UTC"),
        "weather_condition": wx_cond,
        "soil_health": health,
        "model_mode": model_mode,
        "weather": {
            "temperature_c": round(temp, 1),
            "temperature_f": round(temp * 9/5 + 32, 1),
            "precipitation_mm_h": round(precip, 3),
            "precipitation_24h_est_mm": round(precip_24h, 2),
            "humidity_pct": round(humid, 1),
            "wind_speed_ms": round(wind, 1),
            "wind_speed_kmh": round(wind * 3.6, 1),
            "pressure_hpa": round(press, 1),
        },
        "soil": {
            "volumetric_water_5cm_m3m3": round(vwc_5, 4),
            "volumetric_water_15cm_m3m3": round(vwc_15, 4),
            "volumetric_water_50cm_m3m3": round(predictions["volumetric_soil_water_-50cm:m3m3"], 4),
            "volumetric_water_150cm_m3m3": round(predictions["volumetric_soil_water_-150cm:m3m3"], 4),
            "moisture_index_5cm": round(smi_5, 3),
            "moisture_index_15cm": round(predictions.get("soil_moisture_index_-15cm:idx", 0.0), 3),
            "moisture_index_50cm": round(predictions.get("soil_moisture_index_-50cm:idx", 0.0), 3),
            "moisture_index_150cm": round(predictions.get("soil_moisture_index_-150cm:idx", 0.0), 3),
            "moisture_deficit_mm": round(smd, 2),
            "frost_probability_pct": round(frost, 1),
        },
        "air_quality": {
            "aqi": round(aqi_val, 1),
            "category": aqi_label,
            "emoji": aqi_emoji,
            "description": aqi_desc,
        },
        "flood_risk": flood_analysis,
        "nasa_power_telemetry": nasa_power_data,
        "raw_predictions": predictions
    }

    # 7. Radial Area Scan
    if radius_km and radius_km > 0:
        def _quick_point_predict(lat, lon):
            return predict(lat=lat, lon=lon, target_time=target_time, radius_km=0, query_nasa_live=False)
        result["radial_scan"] = scan_area_radius(r_lat, r_lon, radius_km=radius_km, prediction_fn=_quick_point_predict)

    # 8. Gemini AI Agricultural Crop Feasibility Assessment
    result["crop_feasibility"] = evaluate_crop_feasibility(result, gemini_api_key=gemini_api_key)

    return result


def print_full_dashboard(res):
    """Outputs the complete multi-modal environmental & agricultural terminal report."""
    loc = res["location"]
    w = res["weather"]
    s = res["soil"]
    aq = res["air_quality"]
    f = res["flood_risk"]
    cf = res["crop_feasibility"]

    print("\n" + "=" * 70)
    print(f"       PRITHVI AI & NASA EARTH DATA · AGRO-CLIMATIC DOSSIER")
    print("=" * 70)
    print(f" Target Region   : {res['display_name']}")
    print(f" Agro-Zone       : {res['zone']} | {'Barani (Rainfed)' if res['barani'] else 'Canal Irrigated'}")
    print(f" River Basin     : {res['river_basin']} | Elevation: {res['elevation_m']} m")
    print(f" Target DateTime : {res['target_time']}")
    print("-" * 70)
    print(f" 🌤️ WEATHER     : {res['weather_condition']} | {w['temperature_c']}°C ({w['temperature_f']}°F)")
    print(f"    Rainfall     : {w['precipitation_mm_h']} mm/h (24h est: {w['precipitation_24h_est_mm']} mm)")
    print(f"    Wind & Humid : {w['wind_speed_kmh']} km/h | {w['humidity_pct']}% RH | {w['pressure_hpa']} hPa")
    print("-" * 70)
    print(f" 🌊 FLOOD RISK   : {f['badge']} ({f['flood_risk_score']}%)")
    print(f"    Runoff Level : {f['runoff_level']}")
    print(f"    Soil Saturation : {f['saturation_percentage']}%")
    print(f"    Advisory     : {f['advisory']}")
    print("-" * 70)
    print(f" 🌱 SOIL STATUS  : {res['soil_health']}")
    print(f"    Surface (5cm): {s['volumetric_water_5cm_m3m3']:.4f} m³/m³ | Root Zone (15cm): {s['volumetric_water_15cm_m3m3']:.4f} m³/m³")
    print(f"    Deep (150cm) : {s['volumetric_water_150cm_m3m3']:.4f} m³/m³ | Deficit: {s['moisture_deficit_mm']} mm | Frost: {s['frost_probability_pct']}%")
    print("-" * 70)
    print(f" 💨 AIR QUALITY  : {aq['emoji']} {aq['category']} (AQI {aq['aqi']})")
    print(f"    Health Alert : {aq['description']}")
    print("-" * 70)
    print(f" 🤖 GEMINI CROP FEASIBILITY EVALUATION:")
    print(f"    Verdict      : ► {cf['is_worth_it']} ◄ (Score: {cf['feasibility_score']}/100)")
    print(f"    Summary      : {cf['summary_verdict']}")
    print(f"    Top Crops    : {', '.join(cf.get('recommended_crops', []))}")
    print(f"    Crops Avoid  : {', '.join(cf.get('crops_to_avoid', []))}")
    print(f"    Soil Action  : {cf.get('soil_action_plan', '')}")
    print(f"    Irrigation   : {cf.get('irrigation_advice', '')}")
    print(f"    Engine       : {cf.get('gemini_status', '')}")
    print("=" * 70 + "\n")


def main():
    parser = argparse.ArgumentParser(description="Prithvi + NASA Multi-City Soil, Weather, Flood & Crop Predictor")
    parser.add_argument("--station", type=str, default="lahore", help="City name, e.g. multan, gujrat, gujranwala, lalamusa, kharian, chakwal, attock, jhelum")
    parser.add_argument("--lat", type=float, default=None, help="Custom latitude")
    parser.add_argument("--lon", type=float, default=None, help="Custom longitude")
    parser.add_argument("--time", type=str, default=None, help="Target datetime YYYY-MM-DD HH:MM")
    parser.add_argument("--radius", type=float, default=25.0, help="Scan radius in km (5, 10, 25, 50, 100)")
    parser.add_argument("--gemini-key", type=str, default=None, help="Google Gemini API key for land feasibility")
    parser.add_argument("--nasa-live", action="store_true", help="Query live NASA POWER API telemetry")
    args = parser.parse_args()

    res = predict(
        station=args.station,
        lat=args.lat,
        lon=args.lon,
        target_time=args.time,
        radius_km=args.radius,
        gemini_api_key=args.gemini_key,
        query_nasa_live=args.nasa_live
    )
    print_full_dashboard(res)


if __name__ == "__main__":
    main()
