"""
Soil + Weather + Air Quality Dataset Downloader
================================================
Downloads historical data (2016-01-01 → today) for:
  • Islamabad  (lat=33.6844, lon=73.0479)
  • Murree     (lat=33.9070, lon=73.3943)
  • Lahore     (lat=31.5204, lon=74.3587)

Parameters pulled per station:
  Weather   : temperature, precipitation, humidity, wind speed, pressure
  Air Quality: air_quality:idx
  Soil      : volumetric water (5/15/50/150 cm), moisture index (5/15/50/150 cm),
              moisture deficit, soil type, soil frost probability

Output: soil_weather_dataset_ISL_MUR_LHR.csv
"""

import os
import sys
import datetime as dt
import pandas as pd
import meteomatics.api as api
from datetime import datetime

# ── API credentials ────────────────────────────────────────────────────────────
USERNAME = "hackathon_nasa_space_apps_den_thehackers"
PASSWORD = "qn4af2tk391yPO767nUA"

# ── Stations ───────────────────────────────────────────────────────────────────
STATIONS = [
    {"name": "Islamabad", "lat": 33.6844, "lon": 73.0479},
    {"name": "Murree",    "lat": 33.9070, "lon": 73.3943},
    {"name": "Lahore",    "lat": 31.5204, "lon": 74.3587},
]

# ── Parameter groups ───────────────────────────────────────────────────────────
WEATHER_PARAMS = [
    "t_2m:C",
    "precip_1h:mm",
    "relative_humidity_2m:p",
    "wind_speed_10m:ms",
    "msl_pressure:hPa",
]

AQ_PARAMS = [
    "air_quality:idx",
]

SOIL_PARAMS = [
    "volumetric_soil_water_-5cm:m3m3",
    "volumetric_soil_water_-15cm:m3m3",
    "volumetric_soil_water_-50cm:m3m3",
    "volumetric_soil_water_-150cm:m3m3",
    "soil_moisture_index_-5cm:idx",
    "soil_moisture_index_-15cm:idx",
    "soil_moisture_index_-50cm:idx",
    "soil_moisture_index_-150cm:idx",
    "soil_moisture_deficit:mm",
    "soil_type:idx",
    "soil_frost:p",
]

# ── Time range ─────────────────────────────────────────────────────────────────
START    = dt.datetime(2016, 1, 1, tzinfo=dt.timezone.utc)
END      = dt.datetime(2026, 11, 14, tzinfo=dt.timezone.utc)
INTERVAL = dt.timedelta(days=1)   # daily

script_dir = os.path.dirname(os.path.abspath(__file__))
OUTPUT_CSV = os.path.join(script_dir, "soil_weather_dataset_ISL_MUR_LHR.csv")


# ── Helper: chunked query (Meteomatics limits params per call) ─────────────────
def _query_chunked(coords, start, end, interval, params, model="mix", chunk_size=10):
    """Query Meteomatics in chunks of `chunk_size` parameters and join."""
    dfs = []
    for i in range(0, len(params), chunk_size):
        chunk = params[i : i + chunk_size]
        df_chunk = api.query_time_series(
            coords, start, end, interval, chunk, USERNAME, PASSWORD, model=model
        )
        dfs.append(df_chunk)
    result = dfs[0]
    for other in dfs[1:]:
        result = result.join(other, how="left")
    return result


# ── Main download function ─────────────────────────────────────────────────────
def download():
    all_dfs = []

    print(f"\n{'='*70}")
    print(f" Soil + Weather Dataset Downloader")
    print(f" Period : {START.date()} → {END.date()}  |  Interval: daily")
    print(f" Stations: {', '.join(s['name'] for s in STATIONS)}")
    print(f"{'='*70}\n")

    for station in STATIONS:
        name = station["name"]
        coords = [(station["lat"], station["lon"])]
        print(f"[*] Downloading {name} ({station['lat']}, {station['lon']}) ...")

        # --- Weather ---
        print(f"    → Weather parameters ...", end="", flush=True)
        try:
            df_w = _query_chunked(coords, START, END, INTERVAL, WEATHER_PARAMS)
            print(f" OK ({len(df_w):,} rows)")
        except Exception as e:
            print(f" FAILED: {e}")
            df_w = None

        # --- Air Quality ---
        print(f"    → Air quality  ...", end="", flush=True)
        try:
            df_aq = _query_chunked(coords, START, END, INTERVAL, AQ_PARAMS)
            print(f" OK")
        except Exception as e:
            print(f" FAILED (non-fatal): {e}")
            df_aq = None

        # --- Soil ---
        print(f"    → Soil parameters ...", end="", flush=True)
        try:
            df_soil = _query_chunked(coords, START, END, INTERVAL, SOIL_PARAMS)
            print(f" OK")
        except Exception as e:
            print(f" FAILED: {e}")
            df_soil = None

        if df_w is None and df_soil is None:
            print(f"    [!] Skipping {name} — no data retrieved.\n")
            continue

        # --- Merge all parameter groups ---
        df_station = df_w
        if df_aq is not None:
            df_station = df_station.join(df_aq, how="left")
        if df_soil is not None:
            df_station = df_station.join(df_soil, how="left")

        df_station = df_station.reset_index()
        df_station["station_name"] = name
        df_station["lat"]          = station["lat"]
        df_station["lon"]          = station["lon"]

        all_dfs.append(df_station)
        print(f"    [+] {name}: {len(df_station):,} rows with "
              f"{len(df_station.columns)} columns\n")

    if not all_dfs:
        raise RuntimeError("No data downloaded from any station.")

    combined = pd.concat(all_dfs, ignore_index=True)

    # Ensure lat/lon appear as first columns after validdate
    cols = ["station_name", "lat", "lon"]
    remaining = [c for c in combined.columns if c not in cols]
    combined = combined[cols + remaining]

    combined.to_csv(OUTPUT_CSV, index=False)

    print(f"{'='*70}")
    print(f"[✓] Combined dataset saved: {OUTPUT_CSV}")
    print(f"    Total rows    : {len(combined):,}")
    print(f"    Total columns : {len(combined.columns)}")
    print(f"    Stations      : {combined['station_name'].value_counts().to_dict()}")
    print(f"    Columns       : {list(combined.columns)}")
    print(f"{'='*70}\n")

    return OUTPUT_CSV


if __name__ == "__main__":
    csv_path = download()
    print(f"\nDataset ready at: {csv_path}")
    print("Next step → run: python train_soil_weather_ai.py")
