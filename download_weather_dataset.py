"""
Download comprehensive 2010-2026 multi-station weather dataset from Meteomatics API.
Includes Islamabad and key regional coordinates to enable spatial-temporal weather prediction.
"""

import os
import sys
import datetime as dt
import pandas as pd
import meteomatics.api as api

# API credentials from NASA Space Apps Hackathon
USERNAME = "hackathon_nasa_space_apps_den_thehackers"
PASSWORD = "qn4af2tk391yPO767nUA"

# Target stations: Islamabad and regional coordinates
STATIONS = [
    {"name": "Islamabad", "lat": 33.6844, "lon": 73.0479},
    {"name": "Rawalpindi", "lat": 33.5651, "lon": 73.0169},
    {"name": "Murree", "lat": 33.9070, "lon": 73.3943},
    {"name": "Lahore", "lat": 31.5204, "lon": 74.3587},
]

# Weather parameters
PARAMETERS = [
    "t_2m:C",                   # 2m Temperature (°C)
    "precip_1h:mm",             # 1-hour Precipitation (mm)
    "relative_humidity_2m:p",   # Relative Humidity (%)
    "wind_speed_10m:ms",        # 10m Wind Speed (m/s)
    "msl_pressure:hPa"          # Mean Sea Level Pressure (hPa)
]

def download_data(output_file=None):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    if output_file is None:
        output_file = os.path.join(script_dir, "weather_training_dataset_2010_2026.csv")

    start = dt.datetime(2010, 1, 1, tzinfo=dt.timezone.utc)
    end = dt.datetime(2026, 11, 14, tzinfo=dt.timezone.utc)
    interval = dt.timedelta(days=1)

    all_dfs = []

    print(f"[*] Downloading weather data from {start.strftime('%Y-%m-%d')} to {end.strftime('%Y-%m-%d')} (Daily interval)...", flush=True)

    for station in STATIONS:
        coords = [(station["lat"], station["lon"])]
        print(f"  -> Fetching {station['name']} ({station['lat']}, {station['lon']})...", end="", flush=True)
        try:
            df = api.query_time_series(
                coords,
                start,
                end,
                interval,
                PARAMETERS,
                USERNAME,
                PASSWORD,
                model="mix"
            )
            df_reset = df.reset_index()
            df_reset["station_name"] = station["name"]
            all_dfs.append(df_reset)
            print(f" OK ({len(df_reset)} records)", flush=True)
        except Exception as e:
            print(f" FAILED: {e}", flush=True)

    if not all_dfs:
        raise RuntimeError("No data could be downloaded from Meteomatics API.")

    combined_df = pd.concat(all_dfs, ignore_index=True)
    combined_df.to_csv(output_file, index=False)
    print(f"\n[+] Successfully saved {len(combined_df):,} records to: {output_file}", flush=True)
    return output_file

if __name__ == "__main__":
    download_data()
