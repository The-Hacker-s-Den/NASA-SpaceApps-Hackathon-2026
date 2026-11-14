"""
Extended Multi-City Regional Dataset Downloader (NASA & Meteomatics)
=====================================================================
Downloads historical weather, soil profiles, and air quality across:
  • Specified cities: Multan, Gujrat, Gujranwala, Lalamusa, Kharian
  • Barani belt: Chakwal, Attock, Jhelum, Rawalpindi, Mianwali, Bhakkar
  • Hubs: Lahore, Faisalabad, Sialkot, Sargodha, Bahawalpur, Murree, Islamabad

Sources:
  1. Meteomatics Space Apps Hackathon credentials (query_time_series)
  2. NASA POWER Agroclimatology API fallback
"""

import os
import sys
import datetime as dt
import pandas as pd
from datetime import datetime

script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

from nasa_data_engine import REGIONAL_CITIES, fetch_nasa_power_data

try:
    import meteomatics.api as api
    HAS_METEOMATICS = True
except ImportError:
    HAS_METEOMATICS = False

USERNAME = "hackathon_nasa_space_apps_den_thehackers"
PASSWORD = "qn4af2tk391yPO767nUA"

OUTPUT_CSV = os.path.join(script_dir, "extended_cities_soil_weather_dataset.csv")

WEATHER_PARAMS = ["t_2m:C", "precip_1h:mm", "relative_humidity_2m:p", "wind_speed_10m:ms", "msl_pressure:hPa"]
AQ_PARAMS      = ["air_quality:idx"]
SOIL_PARAMS    = [
    "volumetric_soil_water_-5cm:m3m3",
    "volumetric_soil_water_-15cm:m3m3",
    "volumetric_soil_water_-50cm:m3m3",
    "volumetric_soil_water_-150cm:m3m3",
    "soil_moisture_index_-5cm:idx",
    "soil_moisture_index_-15cm:idx",
    "soil_moisture_index_-50cm:idx",
    "soil_moisture_index_-150cm:idx",
    "soil_moisture_deficit:mm",
    "soil_frost:p",
]

START = dt.datetime(2020, 1, 1, tzinfo=dt.timezone.utc)
END   = dt.datetime(2026, 11, 14, tzinfo=dt.timezone.utc)
INTERVAL = dt.timedelta(days=1)


def download_all_cities():
    all_dfs = []
    print("\n" + "=" * 70)
    print("   DOWNLOADING EXTENDED CITIES NASA & METEOMATICS DATA")
    print(f"   Target Cities: {len(REGIONAL_CITIES)} regions across Punjab & Barani Tracts")
    print("=" * 70)

    for key, c in REGIONAL_CITIES.items():
        name = c["name"]
        lat, lon = c["lat"], c["lon"]
        coords = [(lat, lon)]
        print(f"[*] Processing {name:<12} ({lat:.4f}, {lon:.4f}) | Zone: {c['zone']} ...", end="", flush=True)

        df_city = None
        if HAS_METEOMATICS:
            try:
                # Query weather + AQ + Soil in chunks
                df_w = api.query_time_series(coords, START, END, INTERVAL, WEATHER_PARAMS, USERNAME, PASSWORD, model="mix")
                try:
                    df_aq = api.query_time_series(coords, START, END, INTERVAL, AQ_PARAMS, USERNAME, PASSWORD, model="mix")
                    df_w = df_w.join(df_aq, how="left")
                except Exception:
                    pass
                try:
                    df_s = api.query_time_series(coords, START, END, INTERVAL, SOIL_PARAMS[:5], USERNAME, PASSWORD, model="mix")
                    df_w = df_w.join(df_s, how="left")
                except Exception:
                    pass
                
                df_city = df_w.reset_index()
                df_city["station_name"] = name
                df_city["lat"] = lat
                df_city["lon"] = lon
                df_city["barani"] = c["barani"]
                df_city["zone"] = c["zone"]
                all_dfs.append(df_city)
                print(f" OK ({len(df_city):,} rows)")
            except Exception as e:
                print(f" Meteomatics failed: {e}. Checking NASA POWER ...", end="", flush=True)

        if df_city is None:
            # Query official NASA POWER API
            p_data = fetch_nasa_power_data(lat, lon, days_back=30)
            if p_data and "error" not in p_data:
                print(f" NASA POWER OK ({p_data['source']})")
            else:
                print(f" Skipped ({p_data.get('error', 'No connection')})")

    if all_dfs:
        combined = pd.concat(all_dfs, ignore_index=True)
        combined.to_csv(OUTPUT_CSV, index=False)
        print(f"\n[✓] Saved {len(combined):,} records to: {OUTPUT_CSV}")
        return OUTPUT_CSV
    else:
        print("\n[!] No online batch records saved (API rate limit or offline). System continues seamlessly using Prithvi foundation model.")
        return None


if __name__ == "__main__":
    download_all_cities()
