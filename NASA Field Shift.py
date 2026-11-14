
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

# Weather parameters
parameters = [
    "t_2m:C",
    "precip_1h:mm",
    "relative_humidity_2m:p",
    "wind_speed_10m:ms",
    "msl_pressure:hPa"
]

# Historical period (2010 to 2026)
start = dt.datetime(2010, 1, 1, tzinfo=dt.timezone.utc)
end = dt.datetime(2026, 11, 14, tzinfo=dt.timezone.utc)


# Daily interval
interval = dt.timedelta(days=1)

# Retrieve historical weather data
df = api.query_time_series(
    coordinates,
    start,
    end,
    interval,
    parameters,
    username,
    password,
    model="mix"
)

# Export dataset


filename = (f"islamabad_weather_{datetime.now():Date_%d_%m_%Y_Time_%H_%M_%S}.csv")

script_dir = os.path.dirname(os.path.abspath(__file__))
output_path = os.path.join(script_dir, filename)
df.to_csv(output_path, index=True)

print(f"Dataset saved successfully: {filename}")

print(df.head())
print(df.info())
