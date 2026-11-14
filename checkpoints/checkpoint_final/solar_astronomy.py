"""
High-Precision Solar Astronomy Module for NASA Field Shift
===========================================================
Calculates accurate Dawn (Civil Twilight), Sunrise, Solar Noon, Sunset, Dusk,
and current solar arc position for any latitude/longitude in Pakistan (UTC+5).
"""

import math
from datetime import datetime, timezone, timedelta

PKT_OFFSET = timedelta(hours=5)

def calculate_solar_times(lat: float, lon: float, dt: datetime = None) -> dict:
    """
    Computes solar times using standard NOAA astronomical algorithms.
    lat: Latitude in decimal degrees (+ North)
    lon: Longitude in decimal degrees (+ East)
    dt: Local datetime (or UTC, defaults to now in PKT)
    """
    if dt is None:
        # Current time in PKT
        dt = datetime.now(timezone.utc) + PKT_OFFSET
    elif dt.tzinfo is None:
        # Assume already PKT
        dt = dt.replace(tzinfo=timezone(PKT_OFFSET))

    day_of_year = dt.timetuple().tm_yday
    year = dt.year

    # Fractional year in radians
    gamma = 2 * math.pi / 365.25 * (day_of_year - 1 + (dt.hour - 12) / 24.0)

    # Equation of Time (minutes)
    eqtime = 229.18 * (
        0.000075 +
        0.001868 * math.cos(gamma) -
        0.032077 * math.sin(gamma) -
        0.014615 * math.cos(2 * gamma) -
        0.040849 * math.sin(2 * gamma)
    )

    # Solar Declination (radians)
    decl = (
        0.006918 -
        0.399912 * math.cos(gamma) +
        0.070257 * math.sin(gamma) -
        0.006758 * math.cos(2 * gamma) +
        0.000907 * math.sin(2 * gamma) -
        0.002697 * math.cos(3 * gamma) +
        0.00148 * math.sin(3 * gamma)
    )

    lat_rad = math.radians(lat)

    def get_hour_angle(zenith_deg):
        zenith_rad = math.radians(zenith_deg)
        cos_ha = (math.cos(zenith_rad) / (math.cos(lat_rad) * math.cos(decl))) - (math.tan(lat_rad) * math.tan(decl))
        # Clamp to [-1, 1]
        if cos_ha > 1.0:
            return None # Sun never reaches zenith (polar night)
        if cos_ha < -1.0:
            return None # Sun never sets (midnight sun)
        return math.degrees(math.acos(cos_ha))

    # Standard sunrise/sunset: zenith = 90.833° (accounting for atmospheric refraction and solar radius)
    ha_sun = get_hour_angle(90.833)
    # Civil twilight (Dawn / Dusk): zenith = 96.0°
    ha_twilight = get_hour_angle(96.0)

    # Solar noon in local PKT minutes from midnight:
    # Timezone offset from UTC is +5 hours -> 300 minutes.
    # Solar noon occurs when solar time = 12:00.
    # Local Time = Solar Time - 4*lon + 60*timezone_offset - eqtime
    solar_noon_min = 720 - (4.0 * lon) + (60 * 5) - eqtime

    if ha_sun is None:
        ha_sun = 90.0
    if ha_twilight is None:
        ha_twilight = 96.0

    sunrise_min = solar_noon_min - (ha_sun * 4.0)
    sunset_min = solar_noon_min + (ha_sun * 4.0)

    dawn_min = solar_noon_min - (ha_twilight * 4.0)
    dusk_min = solar_noon_min + (ha_twilight * 4.0)

    def min_to_timestr(total_min):
        total_min = total_min % 1440
        h = int(total_min // 60)
        m = int(round(total_min % 60))
        if m == 60:
            h = (h + 1) % 24
            m = 0
        ampm = "AM" if h < 12 else "PM"
        disp_h = h if 1 <= h <= 12 else (h - 12 if h > 12 else 12)
        return f"{disp_h}:{m:02d} {ampm}"

    # Current minute of the day in PKT
    curr_min = dt.hour * 60 + dt.minute

    # Solar position across daytime arc (0% at sunrise, 50% at noon, 100% at sunset)
    day_len_min = max(1.0, sunset_min - sunrise_min)
    if curr_min < sunrise_min:
        sun_pct = 0.0
        is_daylight = False
    elif curr_min > sunset_min:
        sun_pct = 100.0
        is_daylight = False
    else:
        sun_pct = round(((curr_min - sunrise_min) / day_len_min) * 100.0, 1)
        is_daylight = True

    day_hours = int(day_len_min // 60)
    day_mins = int(round(day_len_min % 60))

    return {
        "dawn": min_to_timestr(dawn_min),
        "sunrise": min_to_timestr(sunrise_min),
        "solar_noon": min_to_timestr(solar_noon_min),
        "sunset": min_to_timestr(sunset_min),
        "dusk": min_to_timestr(dusk_min),
        "daylight_duration": f"{day_hours}h {day_mins}m",
        "sun_progress_pct": sun_pct,
        "is_daylight": is_daylight,
        "solar_declination_deg": round(math.degrees(decl), 2),
        "equation_of_time_min": round(eqtime, 2)
    }

if __name__ == "__main__":
    test_cities = [
        ("Lahore", 31.5497, 74.3436),
        ("Islamabad", 33.6844, 73.0479),
        ("Chakwal", 32.9328, 72.8631),
        ("Karachi", 24.8607, 67.0011),
        ("Gwadar", 25.1264, 62.3225),
        ("Murree", 33.9070, 73.3943),
        ("Skardu", 35.2971, 75.6333)
    ]
    print(f"Astronomy calculations for today ({datetime.now().strftime('%Y-%m-%d')}):")
    for name, lat, lon in test_cities:
        res = calculate_solar_times(lat, lon)
        print(f" {name:10s} (lat {lat:5.2f}, lon {lon:5.2f}) -> Dawn: {res['dawn']} | Rise: {res['sunrise']} | Set: {res['sunset']} | Dusk: {res['dusk']} | Day: {res['daylight_duration']} | Sun%: {res['sun_progress_pct']}%")
