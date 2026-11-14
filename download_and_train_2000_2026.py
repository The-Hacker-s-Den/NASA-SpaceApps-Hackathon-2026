"""
Full pipeline: Download 2000-2026 weather data at 4h intervals, then retrain the AI.
Covers Islamabad + regional stations (Rawalpindi, Murree, Lahore).
"""
import os
import sys
import datetime as dt
import pandas as pd
import meteomatics.api as api

script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.append(script_dir)

USERNAME = "hackathon_nasa_space_apps_den_thehackers"
PASSWORD = "qn4af2tk391yPO767nUA"

STATIONS = [
    {"name": "Islamabad",  "lat": 33.6844, "lon": 73.0479},
    {"name": "Rawalpindi", "lat": 33.5651, "lon": 73.0169},
    {"name": "Murree",     "lat": 33.9070, "lon": 73.3943},
    {"name": "Lahore",     "lat": 31.5204, "lon": 74.3587},
]

PARAMETERS = [
    "t_2m:C",
    "precip_1h:mm",
    "relative_humidity_2m:p",
    "wind_speed_10m:ms",
    "msl_pressure:hPa"
]

START = dt.datetime(2000, 1, 1,  tzinfo=dt.timezone.utc)
END   = dt.datetime(2026, 11, 13, tzinfo=dt.timezone.utc)
INTERVAL = dt.timedelta(hours=4)
OUTPUT_CSV = os.path.join(script_dir, "weather_dataset_2000_2026_4h.csv")

def download():
    all_dfs = []
    print(f"[*] Downloading 2000-01-01 → 2026-11-13  (4-hour interval)", flush=True)
    for s in STATIONS:
        coords = [(s["lat"], s["lon"])]
        print(f"  → {s['name']} ({s['lat']}, {s['lon']}) ...", end="", flush=True)
        try:
            df = api.query_time_series(
                coords, START, END, INTERVAL,
                PARAMETERS, USERNAME, PASSWORD, model="mix"
            )
            df = df.reset_index()
            df["station_name"] = s["name"]
            all_dfs.append(df)
            print(f" OK  ({len(df):,} rows)", flush=True)
        except Exception as e:
            print(f" FAILED: {e}", flush=True)

    if not all_dfs:
        raise RuntimeError("No data downloaded.")

    combined = pd.concat(all_dfs, ignore_index=True)
    combined.to_csv(OUTPUT_CSV, index=False)
    print(f"\n[+] Saved {len(combined):,} rows → {OUTPUT_CSV}", flush=True)
    return OUTPUT_CSV

if __name__ == "__main__":
    csv_path = download()

    print("\n[*] Starting model training on 2000-2026 dataset...", flush=True)
    from train_weather_ai import train
    train(data_path=csv_path, epochs=30)
