# 🛰️ NASA Field Shift — Agro-Climatic Decision Support System
### NASA Space Apps Hackathon 2026 · Team: The Hackers Den · Global Agricultural & Climate AI Challenge

[![NASA Space Apps](https://img.shields.io/badge/NASA%20Space%20Apps-2026-blue.svg)](https://www.spaceappschallenge.org/)
[![Team](https://img.shields.io/badge/Team-The%20Hackers%20Den-purple.svg)]()
[![Model](https://img.shields.io/badge/Foundation%20Model-NASA--IBM%20Prithvi%20EO--V2%20300M-emerald.svg)](https://huggingface.co/ibm-nasa-geospatial)
[![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.12%20%7C%203.13-yellow.svg)]()
[![Security](https://img.shields.io/badge/Security-PBKDF2--HMAC--SHA256%20Vault-green.svg)]()
[![Unit Tests](https://img.shields.io/badge/Tests-13%2F13%20Passing%20(100%25)-brightgreen.svg)]()

---

## ⚡ Quick Start (One Command)

Clone the repository and launch the application in a single command:

```bash
git clone https://github.com/The-Hacker-s-Den/NASA-SpaceApps-Hackathon-2026.git && cd NASA-SpaceApps-Hackathon-2026 && run.bat
```

> **Prerequisites:** Python 3.10+ must be installed and available in your system `PATH`. The `run.bat` launcher will automatically create a virtual environment and install all dependencies on first run.

---

## 🌟 Executive Summary

**NASA Field Shift** is an end-to-end, multi-modal agro-climatic intelligence platform engineered for farmers, agronomists, and policy planners across Pakistan and global arid-to-sub-humid agricultural basins.

Developed by **The Hackers Den** for the **NASA Space Apps Hackathon 2026**, the system harmonizes the **NASA-IBM Prithvi Foundation Model (EO-V2 300M)** architecture with NASA Earth Observations (SMAP, GPM IMERG, MODIS Terra/Aqua, Landsat-8/9, ECOSTRESS), AccuWeather live core telemetry, high-precision astronomical solar mechanics, Google Gemini 2.5 Flash generative AI, and a verified **549-species FAO/NASA Crop Catalog database** — all protected by hardware-bound cryptographic security.

The platform outputs **16 AI prediction variables** covering weather, multi-depth soil moisture, air quality, flood hydrology, crop rotation strategies, and agricultural feasibility assessments through both a rich interactive web GUI and a guided CLI wizard.

---

## 🏛️ System Architecture

```
                       [ Field Coordinates: Lat, Lon ]      [ Temporal Target & Season ]
                                      │                                  │
                                      ▼                                  ▼
                       ┌──────────────────────────────┐  ┌──────────────────────────────┐
                       │  Sinusoidal Spatial Encoder  │  │  Sinusoidal Temporal Encoder │
                       │    (64-dim Fourier Embed)    │  │    (64-dim Cyclic Embed)     │
                       └──────────────┬───────────────┘  └──────────────┬───────────────┘
                                      │                                 │
                                      └────────────────┬────────────────┘
                                                       │
                                      ┌────────────────▼────────────────┐
                                      │    137-dim Multimodal Trunk     │
                                      │  (LayerNorm + GELU + ResBlocks) │
                                      └────────────────┬────────────────┘
                                                       │
       ┌───────────────────────────┬───────────────────┴───────────────────┬───────────────────────────┐
       ▼                           ▼                                       ▼                           ▼
┌──────────────┐            ┌──────────────┐                        ┌──────────────┐            ┌──────────────┐
│ Microclimate │            │ Multi-Depth  │                        │ Hydrological │            │  EPA Stomatal│
│  Predictor   │            │ Soil Strata  │                        │  Flood Risk  │            │  Air Quality │
│(Temp, Rain,  │            │(–5, –15, –50,│                        │(Precip surge,│            │(PM2.5, Ozone,│
│ Humidity, P) │            │  –150cm VWC) │                        │ runoff, SMD) │            │  Smog Index) │
└──────┬───────┘            └──────┬───────┘                        └──────┬───────┘            └──────┬───────┘
       │                           │                                       │                           │
       └───────────────────────────┼───────────────────────────────────────┴───────────────────────────┘
                                   │
                                   ▼
        ┌─────────────────────────────────────────────────────────────────────┐
        │       THE HACKERS DEN DECISION ENGINE & INTELLIGENT DISPATCH        │
        ├─────────────────────────────────────────────────────────────────────┤
        │ • CCRS (Crop-Climate Resilience Score: Letter Grade A+ to F)       │
        │ • 549 FAO/NASA Crops Catalog Query Engine (SQLite + Full Indexes)   │
        │ • 4-Depth Soil Water Balance & Deficit Assessment (SMD in mm)       │
        │ • Real-time Solar Astronomy (Dawn, Sunrise, Solar Noon, Sunset)     │
        │ • Dynamic What-If Climate Simulator & Pakistan Climate Analog Match │
        │ • 4 NASA Crop Rotation Scenarios (Water, Regeneration, Income, Pest)│
        │ • Bilingual Farmer Broadcast (Urdu & English)                       │
        │ • Google Gemini 2.5 Flash Agricultural Feasibility Doctor           │
        │ • Hardware-Bound Encrypted Security Vault (AES-256 equivalent)      │
        └──────────────────────────────────┬──────────────────────────────────┘
                                           │
                                           ▼
        ┌─────────────────────────────────────────────────────────────────────┐
        │             HIGH-DEFINITION OBSIDIAN WEB GUI (PORT 5000)            │
        │   Interactive Leaflet Map · Satellite Radar · Downward-Anchored     │
        │   Hourly Forecast · Solar Arch · 549 FAO Crop Catalog Inspector     │
        └─────────────────────────────────────────────────────────────────────┘
```

---

## 🎯 Key Innovation Highlights

### 1. 🧠 NASA-IBM Prithvi Foundation Model Integration

The system is built on the **NASA-IBM Prithvi EO-V2 300M** foundation model architecture. The `LocationEncoder` and `TemporalEncoder` modules from `prithvi_mae.py` generate 64-dimensional sinusoidal Fourier embeddings for spatial coordinates (latitude/longitude) and temporal signals (year/Julian day). These embeddings, combined with 9 cyclic features (sin/cos of hour, day-of-year, and month, plus normalized coordinates), form a **137-dimensional input trunk** that feeds into deep residual blocks with LayerNorm and GELU activations.

Two model architectures are provided:
- **`PrithviWeatherNet`** — 5-target weather backbone (temperature, precipitation, humidity, wind speed, pressure)
- **`PrithviSoilWeatherNet`** — Full 16-target multi-task model adding 10 soil variables and 1 air quality index, with task-specific branches for weather, soil, and air quality

Both models use physically-grounded output heads: `softplus` for non-negative quantities (precipitation, wind, AQI), `sigmoid` scaling for bounded ranges (humidity 0–100%, VWC 0–0.6 m³/m³, frost 0–100%), and `tanh` for soil moisture indices (−1 to +1).

### 2. 🌾 FAO & NASA 549-Species Crops Catalog

- A comprehensive relational SQLite database of **549 verified crop species and cultivars** categorized into 10 agronomic groups (Cereals, Legumes, Vegetables, Fruits, Oilseeds, Roots/Tubers, Spices, Forage, and Production Systems).
- Complete data bindings to NASA Earth Observation sensors: **SMAP L4** (soil moisture), **GPM IMERG** (precipitation), **MODIS NDVI/EVI** (vegetation), **Landsat-9 Thermal Infrared**, and **NASA Harvest Portal**.
- Dual-mode GUI interface: Instant switching between **Local Regional Recommendations** (sowing dates, expected yields, gross margins in PKR) and the **Global 549 Catalog Explorer** with sub-millisecond keyword search and category filtering.
- Interactive slide-over modal detailing growth cycles, optimal temperatures, annual rainfall ranges, soil pH limits, and FAO EcoCrop portal links.

### 3. 🤖 Google Gemini 2.5 Flash Agricultural Doctor

- Integrates **Google Gemini 2.5 Flash** generative AI via the REST API to produce expert agronomic feasibility reports.
- Sends a comprehensive prompt containing all 16 prediction variables (soil VWC at 4 depths, AQI, flood risk score, weather conditions) and receives a structured JSON assessment with:
  - Feasibility verdict (Highly Feasible / Feasible With Precautions / Marginal / Not Recommended)
  - Feasibility score (0–100)
  - Recommended crops and crops to avoid
  - Flood/water risk analysis, smog/air impact, soil action plan, and irrigation advice
- Falls back gracefully to a **built-in Expert Agronomy Rule Engine** modeled after PARC (Pakistan Agricultural Research Council) guidelines when the API is unavailable.

### 4. 🌐 Live Weather Integration (AccuWeather Core API)

- Fetches **12-hour hourly forecasts** and **5-day daily forecasts** from AccuWeather's Core Weather API.
- **39 pre-cached location keys** across all major Pakistani agricultural cities ensure zero-latency lookups.
- Supports geoposition-based search for custom coordinates.
- Falls back to a **Prithvi diurnal solar harmonic cycle** ($T(h) = T_{mean} + \Delta T \cdot \sin(\pi(h-9)/12)$) for temperature synthesis when the API is unavailable or throttled.

### 5. ☀️ Dynamic Astronomical Solar Ephemeris

- Real-time celestial mechanics based on **NOAA solar zenith equations**.
- Computes **Civil Dawn** (zenith 96°), **Sunrise** (zenith 90.833°), **Solar Noon**, **Sunset**, and **Civil Dusk** dynamically for every latitude/longitude across Pakistan (UTC+5).
- Uses the equation of time and solar declination for high-precision results.
- Upward-curving golden solar dome arch in the GUI with real-time sun positioning and nocturnal indicators.

### 6. 🌊 Hydrological Flood Risk & Runoff Modeling

The flood risk engine produces a composite **0–100% Flood Risk Score** by combining five physically-grounded factors:
1. **Rainfall intensity** (0–40 pts) — scaled from 24h/72h precipitation accumulation
2. **Soil saturation** (0–35 pts) — average VWC across the top 15cm relative to field capacity
3. **Moisture deficit buffer** (0–10 pts) — penalizes near-zero SMD (soil at or above field capacity)
4. **Basin vulnerability** (0–15 pts) — city-specific weighting (e.g., Murree: 14 for landslide/runoff, Chakwal: 4 for well-drained plateau)
5. **Topographic elevation** (0–3 pts) — low-lying alluvial plains retain floodwater longer

Categories: 🟢 Minimal/Safe · 🟡 Moderate/Pooling · 🟠 High/Inundation Alert · 🔴 Severe Flood Warning

### 7. 🌱 4-Depth Soil Strata Profile

Predicts volumetric water content (VWC) across four key agricultural rhizosphere depths:

| Depth | Layer | Description |
|-------|-------|-------------|
| –5 cm | Surface | Seed germination & surface evaporation zone |
| –15 cm | Root Zone | Active plant water uptake buffer |
| –50 cm | Subsoil | Deep drainage & nutrient transport layer |
| –150 cm | Deep Aquifer | Groundwater infiltration & capillary rise interface |

Also computes: Soil Moisture Index (SMI: −1 to +1), Soil Moisture Deficit (SMD in mm), and Frost Probability (%).

### 8. 💨 US EPA Air Quality Index (AQI)

Follows the US EPA 6-category standard (0–500 scale):
- 🟢 Good (0–50) · 🟡 Moderate (51–100) · 🟠 Unhealthy for Sensitive (101–150)
- 🔴 Unhealthy (151–200) · 🟣 Very Unhealthy (201–300) · ⚫ Hazardous (301–500)

City-specific calibration accounts for Pakistan's seasonal smog patterns (Oct–Jan) particularly affecting Lahore, Gujranwala, and Faisalabad.

### 9. 🔄 4 NASA Crop Rotation Scenarios

Simulates four distinct rotational strategies dynamically scored against real field conditions:

| Scenario | Focus | Ideal For |
|----------|-------|-----------|
| **A: Water-Conserving** | Drought buffering & moisture retention | Barani rainfed tracts (Chakwal, Attock) |
| **B: Soil Regeneration** | N-fixation & organic matter restoration | Degraded, low-OM soils |
| **C: Maximum Income** | High-value export crop optimization | Irrigated plains (Multan, Lahore) |
| **D: Pest/Weed Disruption** | Disease cycle interruption & erosion defense | Riverine floodplains, weed hotspots |

Each scenario includes a 4-season crop succession cycle with quantified benefits: water savings %, soil N fixed (kg/ha), erosion reduction %, and economic rating.

### 10. 🌡️ Interactive Climate What-If Simulator

- Temperature anomaly slider ($\Delta T$: −3°C to +5°C) and precipitation scaling (0.5× to 2.0× baseline).
- Models cascading effects on soil moisture, flood risk, and evapotranspiration demand using Clausius-Clapeyron thermodynamic relationships.
- **Automatic Pakistan Climate Analog City matching**: recommends the closest real-world analog city based on the simulated climate shift (e.g., Murree for extreme heat, Multan for cold protection, Chakwal for drought).

### 11. 📊 Crop-Climate Resilience Score (CCRS)

A novel composite index (0–100) measuring a parcel's overall agro-climatic survivability, derived from four weighted components:
- Root Zone Resilience (0–35 pts)
- Flood & Runoff Immunity (0–30 pts)
- Atmospheric Clean Air Factor (0–20 pts)
- Moisture Retention Buffer (0–15 pts)

Mapped to letter grades: **A+** (≥90) · **A** (≥80) · **B** (≥68) · **C** (≥55) · **D** (≥40) · **F** (<40), each with a specific adaptation strategy.

### 12. 🇵🇰 Bilingual Farmer Advisory (Urdu & English)

Generates ready-to-read audio broadcast scripts in both **Urdu (اردو)** and **English** for rural farmers in Pakistan via smartphone text-to-speech. Includes crop recommendations, flood status, AQI alerts, and irrigation guidance translated with agricultural terminology localized for Pakistani farming communities.

### 13. 🛡️ Cryptographic Security Vault

- **PBKDF2-HMAC-SHA256 key derivation** with 200,000 rounds and per-record random cryptographic salts.
- **Machine hardware fingerprint binding**: derives encryption keys from `platform.node()`, `platform.machine()`, and `platform.processor()` — prevents vault extraction to external machines.
- **HMAC-SHA256 tamper-evident digital signatures** on every encrypted record with constant-time comparison.
- Encrypted SQLite vault (`nasa_secure_vault.db`) storing field assessments, API keys, user locations, and security events.
- Role-based session tokens with 12-hour expiry and cryptographic signing.
- Immutable security audit trail logging all access, tampering attempts, and authentication events.

### 14. 🛰️ NASA POWER API & GIBS Satellite Integration

- **NASA POWER API** (Langley Research Center): fetches daily agroclimatology records including T2M, PRECTOTCORR, RH2M, WS10M, PS, GWETTOP, GWETROOT, GWETPROF, and ALLSKY_SFC_SW_DWN from MERRA-2/GEOS FP-IT assimilation.
- **NASA GIBS** (Global Imagery Browse Services): provides MODIS Terra TrueColor, VIIRS Night Lights, Blue Marble NextGen, and ESRI satellite tiles for the interactive map widget.

### 15. 📍 40+ Pakistani Agricultural Cities

Complete administrative hierarchy covering **7 provinces/regions** and **40+ cities** with detailed metadata:
- GPS coordinates, elevation, agro-ecological zone classification
- Barani (rainfed) vs. Canal Irrigated designation
- River basin assignment, soil type, and primary crop profiles
- Covers: Punjab (20 cities), Sindh (5), KPK (5), Balochistan (4), ICT (1), AJK (3), Gilgit-Baltistan (2)

### 16. 🗺️ Multi-Point Radial Spatial Scanner

Scans the perimeter surrounding target coordinates at configurable radii (5 km, 10 km, 25 km, 50 km, 100 km) across 9 cardinal and intercardinal bearings. Computes spatial variance for:
- Flood risk gradient across the farm perimeter
- Soil moisture distribution
- Air quality gradients

### 17. 📡 Meteomatics Historical Data Pipeline

A dedicated data download script (`NASA Field Shift.py`) interfaces with the **Meteomatics API** to retrieve historical daily weather data (2010–2026) for training and validation, including temperature, precipitation, humidity, wind speed, and sea-level pressure.

---

## 🖥️ Interactive Web GUI Dashboard

The web GUI (`prithvi_weather_gui.py`) is a state-of-the-art single-page application served on **port 5000** with:

- **Dark obsidian theme** with frosted glassmorphism effects and smooth scroll
- **Leaflet.js interactive map** with 5 switchable satellite layers (Google Hybrid, NASA MODIS Terra, VIIRS Night, Blue Marble, ESRI Aerial)
- **Dynamic radius overlay circle** (5–100 km) on the map
- **Real-time live clock** with Pakistan Standard Time
- **Cascading province → city selector** with instant search bar and auto-suggestions
- **Save/bookmark locations** with quick-switch tray
- **6-pill hourly forecast carousel** anchored at the bottom
- **5-day daily forecast** from AccuWeather Live
- **Tabbed panels**: 5-Day Live · Crops & Agronomy · 549 Crop DB · Soil Strata · What-If Analog · Crop Rotation Cycles
- **Solar dome arch** with real-time sun positioning
- **UV Index gauge** and **EPA AQI leaf indicator**
- **Flood risk gauge** with runoff radar
- **CCRS badge** with letter grade
- **NASA Judge Technical Dossier** modal
- **Scientific Glossary** modal (ET, NDVI, Water Balance, Satellite vs Ground)
- **Temperature unit toggle** (°C / °F)
- **Tailwind CSS**, **Font Awesome 6**, **Google Fonts** (Plus Jakarta Sans, JetBrains Mono, Noto Nastaliq Urdu)

---

## 📂 Project Repository Structure

```
NASA-SpaceApps-Hackathon-2026/
│
├── run.bat                           # One-click launcher for Windows (auto venv + deps + server)
├── run.sh                            # One-click launcher for Linux / macOS
├── requirements.txt                  # Python dependencies (PyTorch, scikit-learn, numpy, pandas, etc.)
├── README.md                         # This file
│
├── ─────────────── CORE APPLICATION ───────────────
│
├── main.py                           # Interactive CLI wizard: location → date → radius → prediction
├── prithvi_weather_gui.py            # Web GUI server (port 5000) — full HTML dashboard & REST API
│
├── ─────────────── AI / ML MODELS ───────────────
│
├── prithvi_weather_model.py          # PrithviWeatherNet: 5-target weather neural network architecture
├── prithvi_soil_weather_model.py     # PrithviSoilWeatherNet: 16-target multi-task neural network
├── prithvi_weather_net.pt            # Trained PyTorch weights (weather backbone)
├── weather_gbm_ensemble.pkl          # Trained Gradient Boosted Ensemble (weather)
├── weather_model_metadata.json       # Training metadata and evaluation metrics
│
├── prithvi/                          # NASA-IBM Prithvi EO-V2 300M foundation model
│   ├── prithvi_mae.py                # LocationEncoder & TemporalEncoder (sinusoidal embeddings)
│   ├── Prithvi_EO_V2_300M.pt         # 300M parameter pretrained checkpoint
│   ├── config.json                   # Model configuration
│   ├── inference.py                  # Prithvi inference pipeline
│   ├── requirements.txt              # Prithvi-specific dependencies
│   ├── README.md                     # Prithvi model documentation
│   ├── assets/                       # Model architecture diagrams
│   └── examples/                     # Sample HLS satellite .tif files (Mexico HLS.S30)
│
├── ─────────────── PREDICTION & DATA ENGINES ───────────────
│
├── predict_soil_weather.py           # Multi-modal prediction orchestrator (Weather + Soil + AQI + Crops)
├── predict_weather.py                # Standalone Prithvi neural network inference engine
├── nasa_data_engine.py               # NASA POWER API, GIBS layers, flood modeling, spatial scanner
├── accuweather_service.py            # AccuWeather 12-hour hourly & 5-day daily forecast service
├── solar_astronomy.py                # NOAA solar ephemeris (dawn, sunrise, noon, sunset, dusk)
│
├── ─────────────── AGRICULTURAL DATABASES ───────────────
│
├── crop_catalog_service.py           # 549 FAO/NASA crops catalog query engine (SQLite)
├── crop_database.sql                 # Raw SQL dump of 549 verified agricultural crops
├── nasa_crops_catalog.db             # Indexed SQLite database for instant crop lookups
├── regional_crops_database.py        # Pakistan regional agronomy (Chakwal, Lahore, Multan, etc.)
│
├── ─────────────── AI ADVISORY & ANALYTICS ───────────────
│
├── gemini_agri_advisor.py            # Google Gemini 2.5 Flash agricultural feasibility doctor
├── nasa_challenge_evaluator.py       # 4 crop rotation scenarios, climate what-if, science glossary
├── nasa_hackathon_innovations.py     # CCRS scoring, bilingual advisory, drainage vector, judge dossier
│
├── ─────────────── LOCATION & SECURITY ───────────────
│
├── location_service.py               # Pakistan 7-province hierarchy, GPS geolocation, city matching
├── security_vault.py                 # PBKDF2-HMAC-SHA256 encrypted database vault
├── nasa_secure_vault.db              # Encrypted SQLite vault for records & API keys
│
├── ─────────────── DATA & TRAINING ───────────────
│
├── NASA Field Shift.py               # Meteomatics API data downloader (2010–2026 historical)
├── download_and_train_2000_2026.py   # Extended training data pipeline
├── download_extended_cities_dataset.py # Multi-city dataset downloader
├── download_soil_weather_dataset.py  # Soil + weather dataset downloader
├── download_weather_dataset.py       # Weather dataset downloader
├── create_final_checkpoint.py        # Checkpoint creation utility
├── import_crop_database.py           # Crop database importer
├── islamabad_weather_*.csv           # Cached Meteomatics weather datasets for Islamabad
│
├── ─────────────── TESTING ───────────────
│
├── test_nasa_challenge_features.py   # Unit tests: rotations, glossary, climate sim, GUI (7 tests)
├── test_soil_aq_predictions.py       # Unit tests: multi-depth soil strata & EPA AQI (3 tests)
├── test_weather_predictions.py       # Unit tests: physical sanity & spatial consistency (3 tests)
│
├── ─────────────── CHECKPOINTS ───────────────
│
├── checkpoints/
│   ├── checkpoint_1/                 # Snapshot baseline (full source + model metadata)
│   └── checkpoint_final/             # Final submission snapshot with all features
│
└── venv/                             # Python virtual environment (machine-specific, not portable)
```

---

## 🚀 How to Run the Application

### Option A: One-Click Launcher (Easiest)

Simply double-click or execute the launcher script in the project root:

- **Windows**: Double-click `run.bat` (or run `.\run.bat` in Command Prompt)
- **Linux / macOS**: Run `chmod +x run.sh && ./run.sh`

The launcher will automatically detect or create the virtual environment, install missing dependencies from `requirements.txt`, and start the server on port 5000.

### Option B: Running on Another PC (Manual Setup)

When copying this project to a new PC (do **not** copy the `venv/` folder, as virtual environments are machine-specific):

1. **Prerequisites**: Ensure Python 3.10+ (recommended 3.11 or 3.12) is installed.
2. **Open Terminal / PowerShell** inside the project folder:
   ```bash
   cd NASA-SpaceApps-Hackathon-2026
   ```
3. **Create a fresh virtual environment**:
   ```bash
   python -m venv venv
   ```
4. **Activate the environment**:
   - **Windows PowerShell**: `.\venv\Scripts\Activate.ps1`
   - **Windows CMD**: `.\venv\Scripts\activate.bat`
   - **macOS / Linux**: `source venv/bin/activate`
5. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
6. **Launch the GUI Server**:
   ```bash
   python prithvi_weather_gui.py --port 5000
   ```
7. **Open in Browser**: Navigate to **[http://127.0.0.1:5000/](http://127.0.0.1:5000/)**

### Option C: Interactive CLI Wizard

Run the full guided wizard (province → city → date range → area range → prediction):
```bash
python main.py
```

### Option D: CLI Prediction Mode

Predict comprehensive weather, soil strata, and agricultural feasibility directly from the terminal:
```powershell
# Chakwal Barani Plateau
python predict_soil_weather.py --station "Chakwal" --radius 25

# Lahore Canal Belt
python predict_soil_weather.py --station "Lahore" --radius 10

# Custom GPS Coordinates
python predict_soil_weather.py --lat 33.6844 --lon 73.0479

# With NASA POWER live telemetry
python predict_soil_weather.py --station "Multan" --radius 50 --nasa-live
```

### Query the 549 Crop Catalog via REST API

```powershell
# Search crops
curl "http://127.0.0.1:5000/api/crop-catalog?q=wheat"

# List distinct crop groups
curl "http://127.0.0.1:5000/api/crop-catalog/groups"

# Inspect single crop detail
curl "http://127.0.0.1:5000/api/crop-catalog/detail?id=CR0002"
```

---

## ⚙️ Dependencies

All dependencies are listed in `requirements.txt`:

| Package | Version | Purpose |
|---------|---------|---------|
| `torch` | ≥ 2.0.0 | PyTorch deep learning framework |
| `torchvision` | latest | Vision utilities |
| `timm` | ≥ 0.9.0 | PyTorch Image Models (Prithvi integration) |
| `einops` | ≥ 0.7.0 | Tensor operations |
| `scikit-learn` | ≥ 1.3.0 | Gradient Boosted Ensemble models |
| `joblib` | ≥ 1.3.0 | Model serialization |
| `numpy` | ≥ 1.24.0 | Numerical computing |
| `pandas` | ≥ 2.0.0 | Data processing & time series |
| `scipy` | ≥ 1.10.0 | Scientific computing |
| `Pillow` | ≥ 9.5.0 | Image processing |
| `requests` | ≥ 2.28.0 | HTTP requests |

---

## 🧪 Comprehensive Verification Suite

Execute the complete **13-test** automated test suite:

```powershell
# 1. NASA Challenge Features & GUI Endpoints (7 tests)
python test_nasa_challenge_features.py

# 2. Multi-Depth Soil Strata & Air Quality (3 tests)
python test_soil_aq_predictions.py

# 3. Neural Network Weather Predictions & Physical Sanity (3 tests)
python test_weather_predictions.py
```

**Verification Status:**

| Test Suite | Tests | Status |
|-----------|-------|--------|
| `test_nasa_challenge_features.py` | 7/7 | ✅ PASSED (100%) |
| `test_soil_aq_predictions.py` | 3/3 | ✅ PASSED (100%) |
| `test_weather_predictions.py` | 3/3 | ✅ PASSED (100%) |
| **Total** | **13/13** | **✅ PASSED (100% Zero Defects)** |

---

## 📡 Data Sources & APIs

| Source | Type | Usage |
|--------|------|-------|
| **NASA POWER API** | Daily agroclimatology (MERRA-2/GEOS) | Temperature, precipitation, humidity, wind, soil wetness, solar radiation |
| **NASA GIBS** | WMTS satellite tiles | MODIS Terra TrueColor, VIIRS Night, Blue Marble, ESRI Aerial |
| **NASA-IBM Prithvi EO-V2** | Foundation model (300M params) | LocationEncoder & TemporalEncoder for spatio-temporal embeddings |
| **NASA SMAP** | Satellite (L-band radiometer) | Soil moisture reference data |
| **NASA GPM IMERG** | Satellite (multi-sensor) | Precipitation estimates |
| **NASA MODIS** | Satellite (Terra/Aqua) | NDVI/EVI vegetation indices |
| **NASA Landsat-8/9** | Satellite (OLI/TIRS) | Land surface temperature, thermal infrared |
| **NASA ECOSTRESS** | Satellite (ISS) | Evapotranspiration & thermal stress |
| **AccuWeather Core API** | Live weather | 12-hour hourly + 5-day daily forecasts |
| **Google Gemini 2.5 Flash** | Generative AI | Agricultural feasibility reports |
| **Meteomatics API** | Historical weather archive | Training data (2010–2026) |
| **FAO EcoCrop / GAEZ** | Agricultural database | 549 crop species parameters |

---

## 🏆 NASA Hackathon Benchmark Metrics

| Metric | Value |
|--------|-------|
| Temperature R² | 0.968 |
| Temperature MAE | 1.21°C |
| Sea Level Pressure R² | 0.935 |
| Relative Humidity R² | 0.803 |
| Soil Volumetric Water R² | 0.884 |
| Prediction Targets | 16 (Weather + Soil + AQI) |
| Crop Catalog Size | 549 species |
| Test Suite Pass Rate | 13/13 (100%) |
| Cities Covered | 40+ across 7 provinces |

---

## 📐 Scientific Glossary

The system includes a built-in explainer for key scientific concepts:

- **Evapotranspiration (ET)**: $ET_c = K_c \times ET_0$ — Combined water loss through soil evaporation and plant transpiration
- **Soil Moisture Anomaly**: $\text{Anomaly} = (VWC_{current} - VWC_{mean}) / \sigma$ — Standard deviation departure from 10-year baseline
- **NDVI**: $\text{NDVI} = (NIR - Red) / (NIR + Red)$ — Vegetation health index from reflectance ratios
- **Water Balance**: $\Delta S = P - ET - R_s - D_d$ — Conservation of water in the agricultural root zone
- **Satellite vs Ground**: Data fusion via Kalman Filter / Prithvi Harmonic Residual Blend

---

## 👥 Hackathon Team

**Team Name:** The Hackers Den  
**Challenge:** NASA Space Apps Hackathon 2026 — Agro-Climatic Decision Support & Future Weather Forecasting  
**Location:** Pakistan / Global  
**Repository:** [github.com/The-Hacker-s-Den/NASA-SpaceApps-Hackathon-2026](https://github.com/The-Hacker-s-Den/NASA-SpaceApps-Hackathon-2026)  
**License:** MIT Open Source License (NASA Space Apps compliant)
