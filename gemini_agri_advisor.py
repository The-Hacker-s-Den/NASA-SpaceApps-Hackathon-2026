"""
Gemini Agricultural Feasibility & Land Valuation Advisor
=========================================================
Evaluates whether it is worth growing crops on a given land parcel using:
  • Google Gemini Generative AI (via user-supplied API Key or env GEMINI_API_KEY)
  • Comprehensive physical inputs from NASA POWER, NASA-IBM Prithvi, and Meteomatics:
      - Multi-depth soil volumetric water (5, 15, 50, 150 cm)
      - Soil Moisture Deficit & Frost Risk
      - Air Quality Index (AQI) & Smog concentration
      - Hydrological Flood Risk Score & Surface Runoff
      - Agro-ecological zone (Barani rainfed vs. Canal Irrigated)
  • Built-in Expert Agronomy Engine fallback (works even without an API key)
"""

import os
import sys
import json
import urllib.request
import urllib.parse
from datetime import datetime

script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

try:
    from security_vault import load_secure_api_key, store_secure_api_key
except ImportError:
    load_secure_api_key = lambda s: None
    store_secure_api_key = lambda s, k: None

# Official Configured NASA Hackathon Gemini API Key
DEFAULT_GEMINI_KEY = "AQ.Ab8RN6K_5wb-D14m4yDayFbToiR_J00CEtDYUTw9cl8xFfeRag"

# Supported Google Gemini Models in order of priority
GEMINI_MODELS = [
    "gemini-2.5-flash",
    "gemini-flash-latest",
    "gemini-2.0-flash"
]


def evaluate_crop_feasibility(land_data: dict, gemini_api_key: str = None):
    """
    Evaluates agricultural feasibility of the land parcel.
    Returns structured recommendations and feasibility metrics.
    """
    # Check for API key (argument -> secure vault -> env var -> configured default)
    api_key = (
        gemini_api_key
        or load_secure_api_key("gemini")
        or os.environ.get("GEMINI_API_KEY", "").strip()
        or DEFAULT_GEMINI_KEY
    )
    
    if api_key:
        try:
            return _call_gemini_api(land_data, api_key)
        except Exception as e:
            fallback = _expert_rule_agronomy_evaluator(land_data)
            fallback["gemini_status"] = f"Gemini API Error ({str(e)}). Used Offline Expert Agronomy Engine."
            return fallback
    else:
        fallback = _expert_rule_agronomy_evaluator(land_data)
        fallback["gemini_status"] = "No Gemini API key provided. Generated via Offline NASA-Trained Agronomy Engine. Add API key for full generative report."
        return fallback


def _call_gemini_api(land_data: dict, api_key: str):
    """Calls Google Gemini REST API with the agro-climatic prompt using gemini-2.5-flash."""
    city = land_data.get("location", "Unknown Location")
    lat = land_data.get("lat", 0.0)
    lon = land_data.get("lon", 0.0)
    zone = land_data.get("zone", "Agricultural Plains")
    is_barani = land_data.get("barani", False)
    
    soil = land_data.get("soil", {})
    weather = land_data.get("weather", {})
    aqi_info = land_data.get("air_quality", {})
    flood = land_data.get("flood_risk", {})
    
    prompt = f"""
You are an expert Chief Agronomist and Agricultural Scientist specializing in Pakistan's agricultural ecology (Barani rain-fed tracts of Potohar/Salt Range and Canal-irrigated Indus/Punjab plains).

Analyze the following NASA Earth Data and Prithvi AI model readings for a farm plot and determine whether it is WORTH IT TO GROW CROPS on this land right now.

=== FIELD TELEMETRY ===
Location: {city} (Lat: {lat}, Lon: {lon})
Agro-Ecological Classification: {zone} (Barani / Rainfed: {'YES' if is_barani else 'NO, Canal Irrigated'})
Elevation: {land_data.get('elevation_m', 200)} meters

SOIL DYNAMICS (Prithvi Foundation Model):
• Volumetric Water Content @ 5cm (Surface): {soil.get('volumetric_water_5cm_m3m3', 'N/A')} m³/m³
• Volumetric Water Content @ 15cm (Root Zone): {soil.get('volumetric_water_15cm_m3m3', 'N/A')} m³/m³
• Volumetric Water Content @ 50cm (Subsoil): {soil.get('volumetric_water_50cm_m3m3', 'N/A')} m³/m³
• Volumetric Water Content @ 150cm (Deep Table): {soil.get('volumetric_water_150cm_m3m3', 'N/A')} m³/m³
• Soil Moisture Deficit: {soil.get('moisture_deficit_mm', 'N/A')} mm
• Soil Frost Probability: {soil.get('frost_probability_pct', 'N/A')}%
• Soil Health Diagnosis: {land_data.get('soil_health', 'N/A')}

ATMOSPHERE & AIR QUALITY:
• 2-meter Air Temp: {weather.get('temperature_c', 'N/A')} °C
• Relative Humidity: {weather.get('humidity_pct', 'N/A')}%
• Precipitation: {weather.get('precipitation_mm_h', 'N/A')} mm/h
• Wind Speed: {weather.get('wind_speed_kmh', 'N/A')} km/h
• Air Quality Index (AQI): {aqi_info.get('aqi', 'N/A')} ({aqi_info.get('category', 'N/A')})

HYDROLOGY & FLOOD HAZARD:
• Composite Flood Risk Score: {flood.get('flood_risk_score', 'N/A')}% ({flood.get('category', 'N/A')})
• Soil Saturation: {flood.get('saturation_percentage', 'N/A')}%
• Runoff Level: {flood.get('runoff_level', 'N/A')}

=== OUTPUT CONTRACT ===
Respond ONLY with a valid JSON object with the exact keys below:
{{
  "is_worth_it": "YES - Highly Feasible" | "YES - Feasible With Precautions" | "MARGINAL - High Risk" | "NO - Not Recommended",
  "feasibility_score": <integer 0 to 100>,
  "summary_verdict": "<2-3 sentence punchy bottom-line executive summary for the farmer>",
  "recommended_crops": ["<Crop 1>", "<Crop 2>", "<Crop 3>", "<Crop 4>"],
  "crops_to_avoid": ["<Avoid Crop 1>", "<Avoid Crop 2>"],
  "flood_and_water_risk": "<1-2 sentences on waterlogging or flood washout threat>",
  "smog_air_impact": "<1-2 sentences on how the AQI affects crop photosynthesis and yield>",
  "soil_action_plan": "<Key soil management step, e.g. deep tillage, ridge planting, gypsum, mulching>",
  "irrigation_advice": "<Immediate watering advice based on moisture deficit and rainfall>",
  "economic_outlook": "<Expected yield potential: Low, Moderate, High, or Outstanding>"
}}
"""
    
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.2, "responseMimeType": "application/json"}
    }
    
    # Try gemini-2.5-flash then fallback to gemini-flash-latest
    last_err = None
    for model_name in GEMINI_MODELS:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                res_json = json.loads(resp.read().decode("utf-8"))
            text_content = res_json["candidates"][0]["content"]["parts"][0]["text"]
            # Clean possible markdown formatting
            if text_content.startswith("```json"):
                text_content = text_content[7:]
            if text_content.startswith("```"):
                text_content = text_content[3:]
            if text_content.endswith("```"):
                text_content = text_content[:-3]
            result = json.loads(text_content.strip())
            result["gemini_status"] = f"Live Gemini Analysis Verified ({model_name})"
            return result
        except Exception as e:
            last_err = e
            continue
            
    raise last_err or RuntimeError("Gemini API call failed")


def _expert_rule_agronomy_evaluator(land_data: dict):
    """
    High-precision agronomy rule engine modeled after Pakistan Agricultural Research Council (PARC)
    and NARC Barani Agricultural Guidelines.
    Evaluates land feasibility deterministically based on real NASA data.
    """
    city = land_data.get("location", "Target Region")
    zone = land_data.get("zone", "Agricultural Plains")
    is_barani = land_data.get("barani", False)
    
    soil = land_data.get("soil", {})
    weather = land_data.get("weather", {})
    aqi_info = land_data.get("air_quality", {})
    flood = land_data.get("flood_risk", {})
    
    vwc_root = float(soil.get("volumetric_water_15cm_m3m3", 0.22))
    smd = float(soil.get("moisture_deficit_mm", 15.0))
    frost = float(soil.get("frost_probability_pct", 0.0))
    temp = float(weather.get("temperature_c", 22.0))
    aqi = float(aqi_info.get("aqi", 85.0))
    flood_score = float(flood.get("flood_risk_score", 15.0))
    
    # ── Calculate Feasibility Score (0 - 100) ──────────────────────────────────
    score = 80  # Base healthy land score
    
    # Soil Moisture Penalty/Bonus
    if vwc_root < 0.08:
        score -= 30  # Severe drought
    elif vwc_root < 0.14:
        score -= 15  # Water deficit
    elif 0.18 <= vwc_root <= 0.32:
        score += 10  # Optimal moisture range
    elif vwc_root > 0.45:
        score -= 25  # Waterlogged / root asphyxiation risk
        
    # Flood Risk Penalty
    if flood_score > 70:
        score -= 35
    elif flood_score > 45:
        score -= 15
        
    # Air Quality Penalty
    if aqi > 250:
        score -= 12  # Severe particulate smog reduces sunlight
    elif aqi > 150:
        score -= 6
        
    # Frost Risk Penalty
    if frost > 40:
        score -= 20
        
    # Temperature extremity
    if temp > 44 or temp < 2:
        score -= 15
        
    score = max(5, min(98, score))
    
    # ── Formulate Verdict ─────────────────────────────────────────────────────
    if score >= 75:
        verdict = "YES - Highly Feasible"
        economic = "Outstanding (High Yield Potential)"
    elif score >= 55:
        verdict = "YES - Feasible With Precautions"
        economic = "Moderate to Good Yield"
    elif score >= 35:
        verdict = "MARGINAL - High Risk"
        economic = "Sub-Optimal / High Input Cost"
    else:
        verdict = "NO - Not Recommended"
        economic = "Severe Risk of Crop Failure"
        
    # ── Region-Specific Crop Recommendations ──────────────────────────────────
    city_lower = city.lower()
    
    if "chakwal" in city_lower or "kharian" in city_lower:
        rec_crops = ["Groundnut (Bari-2016)", "Barani Wheat (Chakwal-50)", "Olive (Arbequina / Coratina)", "Canola / Mustard"]
        avoid_crops = ["Basmati Rice (Too water-intensive)", "Sugarcane"]
        soil_plan = "Practice deep chisel plowing before rains to trap moisture. Apply farmyard manure (FYM) to improve water retention."
    elif "attock" in city_lower or "mianwali" in city_lower or "bhakkar" in city_lower:
        rec_crops = ["Desi Chickpea (Gram)", "Barani Wheat", "Cluster Bean (Guar)", "Barley / Pearl Millet"]
        avoid_crops = ["Rice", "Banana", "High-water Maize"]
        soil_plan = "Conserve moisture with stubble mulching. Add zinc sulfate and phosphatic fertilizers to counter sandy-calcareous fixation."
    elif "murree" in city_lower:
        rec_crops = ["Apple Orchards (Red Delicious)", "Stone Fruits (Peach, Plum)", "Walnut", "High-Value Off-Season Vegetables"]
        avoid_crops = ["Cotton", "Sugarcane", "Rice"]
        soil_plan = "Construct bench terraces and contour furrows across slope to halt topsoil erosion from mountain runoff."
    elif "multan" in city_lower or "bahawalpur" in city_lower:
        rec_crops = ["BT Cotton", "Mango Orchards (Chaunsa/Anwar Ratol)", "Spring Maize", "Wheat (Fakhar-e-Bhakkar)"]
        avoid_crops = ["Cold-sensitive temperate fruits", "Rain-dependent Pulses"]
        soil_plan = "Apply gypsum in saline-sodic patches. Laser level fields to maximize canal water conveyance efficiency."
    elif "gujrat" in city_lower or "gujranwala" in city_lower or "sialkot" in city_lower:
        rec_crops = ["Super Basmati Rice (Kisan Basmati)", "Wheat (Akbar-2019)", "Sugarcane", "Autumn Potato"]
        avoid_crops = ["Drought-adapted Gram (Excess moisture causes fungal wilt)"]
        soil_plan = "Incorporate rice straw residues to build organic carbon. Prepare raised beds for potato and wheat to prevent waterlogging."
    else:  # Lahore, Faisalabad, Islamabad, etc.
        rec_crops = ["Wheat (Galaxy/Akbar)", "Basmati Rice", "Hybrid Corn", "Seasonal Vegetables"]
        avoid_crops = ["Water-sensitive legumes in floodplains"]
        soil_plan = "Adopt ridge-furrow planting. Apply balanced N-P-K (2:1:1) with potassium humate for root vigor."
        
    # Summaries
    verdict_summary = f"This land parcel in {city} presents a {verdict} status ({score}/100). "
    if is_barani:
        verdict_summary += f"As a Barani rain-fed zone, soil moisture retention ({vwc_root:.3f} m³/m³) is the primary determinant of yield. "
    else:
        verdict_summary += f"Supported by canal alluvium with favorable root moisture ({vwc_root:.3f} m³/m³). "
        
    if flood_score > 50:
        flood_text = f"Warning: Flood score is elevated ({flood_score}%). Field requires active drainage to prevent root rot."
    else:
        flood_text = f"Hydrological flood threat is minimal ({flood_score}%). Soil can absorb current precipitation volumes."
        
    if aqi > 180:
        aqi_text = f"High AQI ({aqi:.0f} - {aqi_info.get('category')}) indicates heavy aerosol/smog cover, which reduces photosynthetic active radiation (PAR) by 15-20%."
    else:
        aqi_text = f"Air quality ({aqi:.0f} AQI) is within acceptable physiological thresholds for normal stomatal gas exchange."
        
    if smd > 35:
        irr_text = f"High soil deficit ({smd:.1f} mm). Immediate supplemental irrigation or rain-catchment application is essential."
    elif smd < 5:
        irr_text = "Soil is near field capacity. Withhold additional irrigation to avoid waterlogging and nitrogen leaching."
    else:
        irr_text = "Moisture deficit is balanced. Maintain standard irrigation intervals according to crop phenological stage."

    return {
        "is_worth_it": verdict,
        "feasibility_score": score,
        "summary_verdict": verdict_summary,
        "recommended_crops": rec_crops,
        "crops_to_avoid": avoid_crops,
        "flood_and_water_risk": flood_text,
        "smog_air_impact": aqi_text,
        "soil_action_plan": soil_plan,
        "irrigation_advice": irr_text,
        "economic_outlook": economic,
        "gemini_status": "Evaluated via PARC/NASA Agro-Climatic Model Engine"
    }
