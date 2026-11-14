"""
NASA Data Engine & Multi-City Regional Registry
================================================
Official NASA Earth Science & Atmospheric Data Interface:
  • NASA POWER API (NASA Langley Research Center - Daily Meteorology & Agroclimatology)
  • NASA GIBS (Global Imagery Browse Services - MODIS/VIIRS Satellite Layers)
  • Hydrological Flood Modeling & Soil Saturation Calculations
  • Expanded Regional Registry for Pakistan's Barani and Agricultural Belts
  • Multi-Point Radial Spatial Scanner (5 km - 100 km range)
"""

import os
import sys
import json
import math
import urllib.request
import urllib.parse
from datetime import datetime, timedelta
import numpy as np

# ── OFFICIAL NASA POWER API CONFIGURATION ──────────────────────────────────────
# NASA Prediction Of Worldwide Energy Resources (POWER)
# Source: NASA Langley Research Center (MERRA-2 & GEOS FP-IT assimilation)
NASA_POWER_BASE_URL = "https://power.larc.nasa.gov/api/temporal/daily/point"

# ── COMPREHENSIVE CITY & BARANI REGIONAL REGISTRY ─────────────────────────────
# Enriched with agro-ecological zones, elevation, soil classification, and river basins
REGIONAL_CITIES = {
    # ── User-Specified Cities ──────────────────────────────────────────────────
    "multan": {
        "name": "Multan",
        "display": "Multan (Southern Punjab)",
        "lat": 30.1575,
        "lon": 71.5249,
        "elevation_m": 122,
        "zone": "Arid / Irrigated Plains",
        "river_basin": "Chenab River Basin",
        "primary_crops": ["Cotton", "Mangoes", "Wheat", "Citrus", "Sugarcane"],
        "soil_type": "Alluvial Silt Loam",
        "barani": False
    },
    "gujrat": {
        "name": "Gujrat",
        "display": "Gujrat (Chenab-Jhelum Doab)",
        "lat": 32.5744,
        "lon": 74.0754,
        "elevation_m": 234,
        "zone": "Semi-Arid Alluvial Plain",
        "river_basin": "Chenab River Basin",
        "primary_crops": ["Basmati Rice", "Wheat", "Sugarcane", "Fodder"],
        "soil_type": "Loamy Alluvium",
        "barani": False
    },
    "gujranwala": {
        "name": "Gujranwala",
        "display": "Gujranwala (Majha Rice Belt)",
        "lat": 32.1877,
        "lon": 74.1945,
        "elevation_m": 226,
        "zone": "Sub-Humid Alluvial Plain",
        "river_basin": "Chenab / Ravi Interfluvial Basin",
        "primary_crops": ["Super Basmati Rice", "Wheat", "Potato", "Melons"],
        "soil_type": "Fertile Clay Loam",
        "barani": False
    },
    "lalamusa": {
        "name": "Lalamusa",
        "display": "Lalamusa (Gujrat Plain)",
        "lat": 32.7000,
        "lon": 73.9600,
        "elevation_m": 240,
        "zone": "Semi-Arid Alluvial Plain",
        "river_basin": "Upper Chenab Basin",
        "primary_crops": ["Wheat", "Pearl Millet", "Mustard", "Rice"],
        "soil_type": "Sandy Silt Loam",
        "barani": False
    },
    "kharian": {
        "name": "Kharian",
        "display": "Kharian (Transitional Barani Tract)",
        "lat": 32.8150,
        "lon": 73.8640,
        "elevation_m": 272,
        "zone": "Barani / Semi-Arid Rolling Plain",
        "river_basin": "Upper Jhelum / Chenab Watershed",
        "primary_crops": ["Rainfed Wheat", "Pearl Millet", "Groundnut", "Sorghum"],
        "soil_type": "Sandy Loam to Loess",
        "barani": True
    },

    # ── Core Barani (Rain-Fed) Tracts ──────────────────────────────────────────
    "chakwal": {
        "name": "Chakwal",
        "display": "Chakwal (Core Barani / Potohar)",
        "lat": 32.9328,
        "lon": 72.8631,
        "elevation_m": 498,
        "zone": "Barani Plateau (Rainfed)",
        "river_basin": "Soan River Basin / Potohar Watershed",
        "primary_crops": ["Groundnut (Peanut)", "Olive", "Barani Wheat", "Canola / Mustard", "Chickpea"],
        "soil_type": "Calcareous Loess & Sandy Loam",
        "barani": True
    },
    "attock": {
        "name": "Attock",
        "display": "Attock (Northern Barani Plateau)",
        "lat": 33.7667,
        "lon": 72.3667,
        "elevation_m": 355,
        "zone": "Barani Plateau & Indus Basin",
        "river_basin": "Indus / Haro River Basin",
        "primary_crops": ["Chickpea (Gram)", "Barani Wheat", "Groundnut", "Barley", "Lentil"],
        "soil_type": "Shallow Gravelly to Silt Loam",
        "barani": True
    },
    "jhelum": {
        "name": "Jhelum",
        "display": "Jhelum (Riverine Barani)",
        "lat": 32.9405,
        "lon": 73.7276,
        "elevation_m": 233,
        "zone": "Riverine & Sub-Humid Barani",
        "river_basin": "Jhelum River Basin",
        "primary_crops": ["Wheat", "Maize", "Groundnut", "Mustard", "Fodder"],
        "soil_type": "Alluvial Loam & Silt",
        "barani": True
    },
    "rawalpindi": {
        "name": "Rawalpindi",
        "display": "Rawalpindi (Potohar Barani Basin)",
        "lat": 33.5651,
        "lon": 73.0169,
        "elevation_m": 508,
        "zone": "Sub-Humid Barani Plateau",
        "river_basin": "Soan River / Nullah Lai Basin",
        "primary_crops": ["Rainfed Wheat", "Maize", "Fodder", "Vegetables"],
        "soil_type": "Deep Loess Silt Loam",
        "barani": True
    },
    "mianwali": {
        "name": "Mianwali",
        "display": "Mianwali (Thal Barani / Desert Fringe)",
        "lat": 32.5839,
        "lon": 71.5370,
        "elevation_m": 210,
        "zone": "Arid Barani / Thal Sand Plains",
        "river_basin": "Indus River Basin (East Bank)",
        "primary_crops": ["Gram (Chickpea)", "Guar", "Barani Wheat", "Barley"],
        "soil_type": "Aeolian Sand & Sandy Loam",
        "barani": True
    },
    "bhakkar": {
        "name": "Bhakkar",
        "display": "Bhakkar (Thal Core Barani)",
        "lat": 31.6253,
        "lon": 71.0657,
        "elevation_m": 159,
        "zone": "Arid Desert Barani",
        "river_basin": "Thal Internal Drainage / Indus Plains",
        "primary_crops": ["Chickpea (Gram)", "Cluster Bean", "Millet", "Watermelon"],
        "soil_type": "Deep Sandy Desert Soils",
        "barani": True
    },

    # ── Original Backbone Cities ───────────────────────────────────────────────
    "islamabad": {
        "name": "Islamabad",
        "display": "Islamabad (Margalla Sub-Humid)",
        "lat": 33.6844,
        "lon": 73.0479,
        "elevation_m": 540,
        "zone": "Sub-Humid Foothills",
        "river_basin": "Korang / Soan River Basin",
        "primary_crops": ["Wheat", "Horticulture", "Olive Orchards", "Vegetables"],
        "soil_type": "Silt Loam & Colluvial",
        "barani": True
    },
    "murree": {
        "name": "Murree",
        "display": "Murree (High-Altitude Mountain Watershed)",
        "lat": 33.9070,
        "lon": 73.3943,
        "elevation_m": 2291,
        "zone": "Humid Mountain Ecosystem",
        "river_basin": "Jhelum / Haro Mountain Catchment",
        "primary_crops": ["Apples", "Stone Fruits (Peach, Plum)", "Walnut", "Maize"],
        "soil_type": "Mountain Forest Soil (Humus Rich)",
        "barani": True
    },
    "lahore": {
        "name": "Lahore",
        "display": "Lahore (Ravi Alluvial Plain)",
        "lat": 31.5204,
        "lon": 74.3587,
        "elevation_m": 217,
        "zone": "Semi-Arid Irrigated Plain",
        "river_basin": "Ravi River Basin",
        "primary_crops": ["Wheat", "Rice", "Maize", "Fodder", "Vegetables"],
        "soil_type": "Old Alluvial Silt Loam",
        "barani": False
    },

    # ── Additional Major Agricultural Hubs ────────────────────────────────────
    "faisalabad": {
        "name": "Faisalabad",
        "display": "Faisalabad (Canal Agricultural Capital)",
        "lat": 31.4504,
        "lon": 73.1350,
        "elevation_m": 186,
        "zone": "Semi-Arid Canal Irrigated",
        "river_basin": "Chenab-Ravi (Rechna Doab)",
        "primary_crops": ["Wheat", "Sugarcane", "Cotton", "Maize", "Rice"],
        "soil_type": "Deep Fertile Calcareous Loam",
        "barani": False
    },
    "sialkot": {
        "name": "Sialkot",
        "display": "Sialkot (Upper Chenab Rice Basin)",
        "lat": 32.4945,
        "lon": 74.5229,
        "elevation_m": 256,
        "zone": "Sub-Humid Floodplain",
        "river_basin": "Chenab / Aik & Dek Nullahs Basin",
        "primary_crops": ["Premium Basmati Rice", "Wheat", "Sugarcane", "Potato"],
        "soil_type": "Heavy Clay Loam Alluvium",
        "barani": False
    },
    "sargodha": {
        "name": "Sargodha",
        "display": "Sargodha (Citrus / Kinnow Belt)",
        "lat": 32.0836,
        "lon": 72.6711,
        "elevation_m": 187,
        "zone": "Semi-Arid Jech Doab",
        "river_basin": "Jhelum-Chenab Doab",
        "primary_crops": ["Kinnow (Mandarin)", "Citrus", "Sugarcane", "Wheat", "Rice"],
        "soil_type": "Silt Loam to Silty Clay",
        "barani": False
    },
    "bahawalpur": {
        "name": "Bahawalpur",
        "display": "Bahawalpur (Southern Agro-Desert Fringe)",
        "lat": 29.3956,
        "lon": 71.6833,
        "elevation_m": 115,
        "zone": "Arid Irrigated & Cholistan Transition",
        "river_basin": "Sutlej River Basin",
        "primary_crops": ["Cotton", "Wheat", "Sunflower", "Mustard", "Dates"],
        "soil_type": "Alluvial Loam & Desert Sand",
        "barani": False
    }
}


# ── NASA GIBS (GLOBAL IMAGERY BROWSE SERVICES) SATELLITE TILES ────────────────
# Official NASA WMTS / XYZ satellite tile templates for high-resolution interactive mapping
NASA_GIBS_LAYERS = {
    "modis_truecolor": {
        "name": "NASA MODIS Terra (TrueColor Satellite)",
        "url": "https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/MODIS_Terra_CorrectedReflectance_TrueColor/default/{date}/GoogleMapsCompatible_Level9/{z}/{y}/{x}.jpg",
        "attribution": "NASA Earth Science Data / GIBS / EOSDIS",
        "max_zoom": 9
    },
    "viirs_night": {
        "name": "NASA VIIRS Earth at Night",
        "url": "https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/VIIRS_CityLights_2012/default/GoogleMapsCompatible_Level8/{z}/{y}/{x}.jpg",
        "attribution": "NASA GIBS / Suomi NPP / NOAA",
        "max_zoom": 8
    },
    "blue_marble": {
        "name": "NASA Blue Marble NextGen",
        "url": "https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/BlueMarble_NextGeneration/default/GoogleMapsCompatible_Level8/{z}/{y}/{x}.jpeg",
        "attribution": "NASA Earth Observatory",
        "max_zoom": 8
    },
    "esri_satellite": {
        "name": "ESRI World Imagery (High-Res Aerial)",
        "url": "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        "attribution": "Esri, Maxar, Earthstar Geographics",
        "max_zoom": 19
    },
    "osm": {
        "name": "OpenStreetMap Carto",
        "url": "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
        "attribution": "© OpenStreetMap contributors",
        "max_zoom": 19
    }
}


# ── FETCH REAL DATA FROM NASA POWER API ───────────────────────────────────────
def fetch_nasa_power_data(lat: float, lon: float, days_back: int = 5):
    """
    Fetches official daily agro-meteorological records directly from NASA Langley Research Center.
    Parameters queried:
      • T2M          : 2-meter air temperature (°C)
      • PRECTOTCORR  : Corrected total precipitation (mm/day)
      • RH2M         : Relative humidity at 2m (%)
      • WS10M        : Wind speed at 10m (m/s)
      • PS           : Surface pressure (kPa)
      • GWETTOP      : Surface soil wetness (0 to 1 ratio)
      • GWETROOT     : Root zone soil wetness (0 to 1 ratio)
      • GWETPROF     : Profile soil wetness (0 to 1 ratio)
      • ALLSKY_SFC_SW_DWN : Solar insolation incident on horizontal surface (MJ/m^2/day)
    """
    end_date = datetime.utcnow() - timedelta(days=2)  # NASA POWER updates with ~2 day latency
    start_date = end_date - timedelta(days=days_back)
    
    start_str = start_date.strftime("%Y%m%d")
    end_str = end_date.strftime("%Y%m%d")
    
    params = "T2M,PRECTOTCORR,RH2M,WS10M,PS,GWETTOP,GWETROOT,GWETPROF,ALLSKY_SFC_SW_DWN"
    url = f"{NASA_POWER_BASE_URL}?parameters={params}&community=AG&longitude={lon:.4f}&latitude={lat:.4f}&start={start_str}&end={end_str}&format=JSON"
    
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "NASA-SpaceApps-PrithviAI/2.0"})
        with urllib.request.urlopen(req, timeout=12) as response:
            payload = json.loads(response.read().decode())
            
        data = payload.get("properties", {}).get("parameter", {})
        if not data:
            return None
        
        # Extract latest non-null values
        latest_vals = {}
        for p_key, daily_dict in data.items():
            valid_items = [(k, v) for k, v in sorted(daily_dict.items()) if v != -999.0]
            if valid_items:
                latest_vals[p_key] = valid_items[-1][1]
                # Also store total precipitation over the query window for flood accumulation
                if p_key == "PRECTOTCORR":
                    precip_sum = sum(v for _, v in valid_items)
                    latest_vals["PRECTOT_ACCUM"] = round(precip_sum, 2)
            else:
                latest_vals[p_key] = None
                
        return {
            "source": "NASA Langley Research Center (POWER Daily API v2.10)",
            "start_date": start_str,
            "end_date": end_str,
            "latest_date": valid_items[-1][0] if valid_items else end_str,
            "temperature_c": latest_vals.get("T2M"),
            "precipitation_mm_day": latest_vals.get("PRECTOTCORR"),
            "precipitation_accum_mm": latest_vals.get("PRECTOT_ACCUM", 0.0),
            "humidity_pct": latest_vals.get("RH2M"),
            "wind_speed_ms": latest_vals.get("WS10M"),
            "pressure_kpa": latest_vals.get("PS"),
            "surface_wetness_ratio": latest_vals.get("GWETTOP"),
            "root_zone_wetness_ratio": latest_vals.get("GWETROOT"),
            "profile_wetness_ratio": latest_vals.get("GWETPROF"),
            "solar_radiation_mj_m2": latest_vals.get("ALLSKY_SFC_SW_DWN"),
        }
    except Exception as e:
        return {"error": str(e), "source": "NASA POWER API (Temporarily Offline or Timeout)"}


# ── HYDROLOGICAL FLOOD RISK & RUNOFF ESTIMATOR ─────────────────────────────────
def calculate_flood_risk(lat: float, lon: float, precip_accum_mm: float, 
                         vwc_5cm: float, vwc_15cm: float, smd_mm: float,
                         elevation_m: float = 200.0, city_info: dict = None):
    """
    Computes a physically-grounded Flood Risk Index (0 - 100%) and surface runoff potential.
    Combines:
      1. Antecedent Precipitation (24h-72h rainfall accumulation from NASA data)
      2. Soil Profile Saturation (Surface & root zone volumetric water content vs soil capacity)
      3. Soil Moisture Deficit (Near 0 deficit = zero infiltration capacity)
      4. River Basin / Flash Flood Vulnerability Factor (Proximity to major rivers / hill torrents)
      5. Topographic Elevation Factor (Low elevation / alluvial plains retain water longer)
    """
    # 1. Rainfall intensity score (0 to 40 pts)
    # 0mm = 0 pts; 50mm = 20 pts; 100mm+ = 40 pts
    rain_score = min(40.0, (precip_accum_mm / 100.0) * 40.0)
    
    # 2. Soil Saturation score (0 to 35 pts)
    # Average VWC across top 15cm; saturated soil in Punjab loams is ~0.45 - 0.50 m3/m3
    avg_vwc = (vwc_5cm + vwc_15cm) / 2.0
    saturation_ratio = min(1.0, max(0.0, (avg_vwc - 0.10) / 0.35))
    saturation_score = saturation_ratio * 35.0
    
    # 3. Moisture Deficit buffer reduction (0 to 10 pts)
    # Less than 10mm deficit means soil is at field capacity or waterlogged
    deficit_score = 10.0 if smd_mm < 5.0 else max(0.0, (1.0 - smd_mm / 50.0) * 10.0)
    
    # 4. Basin & Topographic Vulnerability (0 to 15 pts)
    # High-risk riverine flood zones or flash-flood nullahs (e.g. Sialkot, Gujrat, Rawalpindi Lai)
    basin_weight = 5.0
    if city_info:
        name = city_info.get("name", "").lower()
        if name in ["sialkot", "gujrat", "rawalpindi", "lahore"]:
            basin_weight = 12.0  # Vulnerable to Chenab/Ravi floods or Nullah Lai flash floods
        elif name in ["multan", "jhelum", "bahawalpur"]:
            basin_weight = 9.0   # Riverine flood plain
        elif name in ["murree"]:
            basin_weight = 14.0  # Extreme mountain runoff / landslide hazard
        elif name in ["chakwal", "attock", "mianwali", "bhakkar"]:
            basin_weight = 4.0   # Well-drained rolling plateau or desert
    
    if elevation_m < 200:
        topo_score = 3.0
    else:
        topo_score = 0.0
        
    total_flood_score = round(min(100.0, max(0.0, rain_score + saturation_score + deficit_score + basin_weight + topo_score)), 1)
    
    # Categorization
    if total_flood_score < 25.0:
        category = "Minimal / Safe"
        badge = "🟢 Safe"
        runoff_level = "Low Infiltration Runoff"
        desc = "Soil has high absorption capacity. Normal drainage with negligible flood threat to crops."
    elif total_flood_score < 50.0:
        category = "Moderate / Low-Lying Pooling"
        badge = "🟡 Moderate"
        runoff_level = "Moderate Surface Ponding"
        desc = "Water will accumulate in low-lying depressions and furrow fields. Monitor sensitive crop roots for waterlogging."
    elif total_flood_score < 75.0:
        category = "High / Inundation Alert"
        badge = "🟠 High Alert"
        runoff_level = "High Sheet Runoff"
        desc = "High runoff potential. Critical risk of root suffocation, field submergence, and bund breaching in agricultural tracts."
    else:
        category = "Severe / Flood Warning"
        badge = "🔴 Severe Flood Warning"
        runoff_level = "Extreme Runoff & Flash Flood"
        desc = "Severe hazard! Active riverine overflow or torrent surge. Crops at high risk of total washout. Clear drainage paths immediately."
        
    return {
        "flood_risk_score": total_flood_score,
        "category": category,
        "badge": badge,
        "runoff_level": runoff_level,
        "advisory": desc,
        "saturation_percentage": round(saturation_ratio * 100.0, 1),
        "rainfall_accumulation_mm": round(precip_accum_mm, 2)
    }


# ── MULTI-POINT RADIAL SPATIAL SCANNER ─────────────────────────────────────────
def scan_area_radius(center_lat: float, center_lon: float, radius_km: float = 25.0, 
                     prediction_fn = None):
    """
    Scans the perimeter and surrounding agricultural area around the target coordinates
    at radius R (5 km, 10 km, 25 km, 50 km, 100 km).
    Computes spatial variance:
      • Flood risk gradient
      • Soil moisture distribution across the farm perimeter
      • Air quality gradient
    """
    # 1 degree latitude ~ 111.0 km
    d_lat = radius_km / 111.0
    cos_lat = math.cos(math.radians(center_lat))
    d_lon = radius_km / (111.0 * max(0.1, cos_lat))
    
    diag = 0.7071  # sin(45 deg)
    
    points = [
        {"bearing": "Center",    "lat": center_lat,           "lon": center_lon},
        {"bearing": "North",     "lat": center_lat + d_lat,   "lon": center_lon},
        {"bearing": "North-East","lat": center_lat + d_lat*diag, "lon": center_lon + d_lon*diag},
        {"bearing": "East",      "lat": center_lat,           "lon": center_lon + d_lon},
        {"bearing": "South-East","lat": center_lat - d_lat*diag, "lon": center_lon + d_lon*diag},
        {"bearing": "South",     "lat": center_lat - d_lat,   "lon": center_lon},
        {"bearing": "South-West","lat": center_lat - d_lat*diag, "lon": center_lon - d_lon*diag},
        {"bearing": "West",      "lat": center_lat,           "lon": center_lon - d_lon},
        {"bearing": "North-West","lat": center_lat + d_lat*diag, "lon": center_lon - d_lon*diag},
    ]
    
    results = []
    moistures = []
    flood_risks = []
    aqi_values = []
    
    for pt in points:
        res = prediction_fn(lat=pt["lat"], lon=pt["lon"]) if prediction_fn else None
        
        # Synthetic / computed default values if offline
        vwc = res.get("soil", {}).get("volumetric_water_5cm_m3m3", 0.22) if res else 0.22
        aqi = res.get("air_quality", {}).get("aqi", 85.0) if res else 85.0
        precip = res.get("weather", {}).get("precipitation_mm_h", 0.0) if res else 0.0
        
        f_risk = calculate_flood_risk(
            lat=pt["lat"], lon=pt["lon"],
            precip_accum_mm=precip * 24.0,
            vwc_5cm=vwc,
            vwc_15cm=vwc,
            smd_mm=res.get("soil", {}).get("moisture_deficit_mm", 15.0) if res else 15.0
        )
        
        entry = {
            "bearing": pt["bearing"],
            "lat": round(pt["lat"], 4),
            "lon": round(pt["lon"], 4),
            "distance_km": 0.0 if pt["bearing"] == "Center" else round(radius_km, 1),
            "soil_water_5cm": round(vwc, 4),
            "aqi": round(aqi, 1),
            "flood_score": f_risk["flood_risk_score"],
            "flood_category": f_risk["category"]
        }
        results.append(entry)
        moistures.append(vwc)
        flood_risks.append(f_risk["flood_risk_score"])
        aqi_values.append(aqi)
        
    return {
        "radius_km": radius_km,
        "sample_count": len(results),
        "soil_moisture_stats": {
            "mean": round(float(np.mean(moistures)), 4),
            "min": round(float(np.min(moistures)), 4),
            "max": round(float(np.max(moistures)), 4),
            "spread": round(float(np.max(moistures) - np.min(moistures)), 4)
        },
        "flood_risk_stats": {
            "mean": round(float(np.mean(flood_risks)), 1),
            "min": round(float(np.min(flood_risks)), 1),
            "max": round(float(np.max(flood_risks)), 1),
            "max_bearing": results[int(np.argmax(flood_risks))]["bearing"]
        },
        "aqi_stats": {
            "mean": round(float(np.mean(aqi_values)), 1),
            "min": round(float(np.min(aqi_values)), 1),
            "max": round(float(np.max(aqi_values)), 1)
        },
        "spatial_samples": results
    }
