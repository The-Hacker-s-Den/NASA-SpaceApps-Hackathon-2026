import datetime as dt
import pandas as pd
import meteomatics.api as api
import os
from datetime import datetime

# API credentials
username = "hackathon_nasa_space_apps_den_thehackers"
password = "qn4af2tk391yPO767nUA"

# Islamabad coordinates
coordinates = [(33.6844, 73.0479)]

# Separated parameters by historical availability
weather_parameters = [
    "t_2m:C",
    "precip_1h:mm",
    "relative_humidity_2m:p",
    "wind_speed_10m:ms",
    "msl_pressure:hPa"
]
aq_parameters = ["air_quality:idx"]

# Time ranges
weather_start = dt.datetime(2016, 1, 1, tzinfo=dt.timezone.utc)
aq_start = dt.datetime(2016, 1, 1, tzinfo=dt.timezone.utc)
end = dt.datetime(2026, 11, 14, tzinfo=dt.timezone.utc)
interval = dt.timedelta(days=1)

# Retrieve historical weather data
df_weather = api.query_time_series(
    coordinates,
    weather_start,
    end,
    interval,
    weather_parameters,
    username,
    password,
    model="mix"
)

# Retrieve historical air quality data
df_aq = api.query_time_series(
    coordinates,
    aq_start,
    end,
    interval,
    aq_parameters,
    username,
    password,
    model="mix"
)

# Merge datasets (populates NaN for air_quality:idx prior to 2015-11-22)
df = df_weather.join(df_aq, how="left")

# Export dataset
filename = f"islamabad_weather_{datetime.now():Date_%d_%m_%Y_Time_%H_%M_%S}.csv"
script_dir = os.path.dirname(os.path.abspath(__file__))
output_path = os.path.join(script_dir, filename)
df.to_csv(output_path, index=True)

print(f"Dataset saved successfully: {filename}")
print(df.head())
print(df.info())