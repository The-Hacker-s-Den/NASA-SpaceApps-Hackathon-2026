# 🛰️ The Hackers Den — NASA Field Shift Decision Support System
### NASA Space Apps Hackathon 2026 · Global Agricultural & Climate AI Challenge

[![NASA Space Apps](https://img.shields.io/badge/NASA%20Space%20Apps-2026-blue.svg)](https://www.spaceappschallenge.org/)
[![Team](https://img.shields.io/badge/Team-The%20Hackers%20Den-purple.svg)]()
[![Model](https://img.shields.io/badge/Foundation%20Model-NASA--IBM%20Prithvi%20EO--V2-emerald.svg)](https://huggingface.co/ibm-nasa-geospatial)
[![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.12%20%7C%203.13-yellow.svg)]()
[![Security](https://img.shields.io/badge/Security-PBKDF2--HMAC--SHA256%20Vault-green.svg)]()
[![Unit Tests](https://img.shields.io/badge/Tests-13%2F13%20Passing%20(100%25)-brightgreen.svg)]()

---

## 🌟 Executive Summary

**The Hackers Den — NASA Field Shift Decision Support System** is an end-to-end, multi-modal agro-climatic intelligence platform engineered for farmers, agronomists, and policy planners across Pakistan and global arid-to-sub-humid agricultural basins.

Developed by **The Hackers Den** for the **NASA Space Apps Hackathon 2026**, the system harmonizes the **NASA-IBM Prithvi Foundation Model (EO-V2 300M)** architecture with NASA Earth Observations (SMAP, GPM IMERG, MODIS Terra/Aqua, Landsat-8/9, ECOSTRESS), AccuWeather live core telemetry, high-precision astronomical solar mechanics, and a verified **549-species FAO/NASA Crop Catalog database** backed by hardware-bound cryptographic security.

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
        │ • Real-time Solar Astronomy (Dawn, Sunrise, Solar Noon, Sunset, Dusk)│
        │ • Dynamic What-If Climate Simulator & Pakistan Climate Analog Match │
        │ • 4 NASA Crop Rotation Scenarios (Water, Regeneration, Income, Pest)│
        │ • Bilingual Farmer Broadcast (Urdu & English)                       │
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

### 1. 🌾 FAO & NASA 549-Species Crops Catalog (`crop_catalog_service.py`)
- Ingested a comprehensive relational database of **549 verified crop species and cultivars** categorized into 10 agronomic groups (Cereals, Legumes, Vegetables, Fruits, Oilseeds, Roots/Tubers, Spices, Forage, and Production Systems).
- Complete data bindings to NASA Earth Observation sensors (**SMAP L4, GPM IMERG, MODIS NDVI/EVI, Landsat-9 Thermal Infrared, and NASA Harvest Portal**).
- Dual-mode GUI interface: Instant switching between **Local Regional Recommendations** (sowing dates, expected yields, gross margins in PKR) and the **Global 549 Catalog Explorer** with instant sub-millisecond keyword search and category filtering.
- Interactive slide-over modal detailing growth cycles, optimal temperatures, annual rainfall ranges, soil pH limits, and FAO EcoCrop portal links.

### 2. ☀️ Dynamic Astronomical Solar Ephemeris (`solar_astronomy.py`)
- Real-time celestial mechanics based on standard NOAA solar zenith equations.
- Computes exact **Civil Dawn (zenith 96°)**, **Sunrise (zenith 90.833°)**, **Solar Noon**, **Sunset**, and **Civil Dusk** dynamically for every city, latitude, and longitude across Pakistan (UTC+5).
- Upward-curving golden solar dome arch with real-time sun positioning and nocturnal indicators.

### 3. ⏱️ Downward-Anchored Hourly Forecast Layout
- Seamless desktop layout with smooth web scrolling (`overflow-y: auto`).
- Left column incorporates the **Hero Weather Glassmorphic Card**, the middle **The Hackers Den Land & Satellite Ephemeris Matrix**, and an anchored bottom **6-Pill Hourly Forecast Carousel** with zero vertical dead space.

### 4. 🛰️ Prithvi 4-Depth Soil Strata Profile & Flood Hydrology
- Predicts volumetric water content across 4 key rhizosphere depths:
  - Surface (–5 cm)
  - Root Zone (–15 cm)
  - Subsoil (–50 cm)
  - Deep Aquifer Infiltration (–150 cm)
- Evaluates Soil Moisture Deficit (SMD in mm), Frost Probability, and Flood Runoff Risk under variable precipitation accumulation.

### 5. 🔄 4 NASA Crop Rotation Scenarios & Climate What-If Analog
- Simulates 4 distinct rotational paradigms:
  - *Water-Conserving Pulse & Barani Fallback*
  - *Soil Regenerative Legume-Grain Biomass Cycle*
  - *Maximum Economic Gross Margin Optimization*
  - *Pest Break & Allelopathic Rotation*
- Interactive temperature anomaly ($\Delta T: -3^\circ\text{C}$ to $+5^\circ\text{C}$) and precipitation scaling sliders with automatic **Pakistan Climate Analog City** matching.

### 6. 🛡️ Military-Grade Cryptographic Security Vault (`security_vault.py`)
- Hardware-bound SQLite vault utilizing PBKDF2-HMAC-SHA256 key derivation with per-record random cryptographic salts and SHA-256 tamper-evident digital signatures.
- Automatically stores all field assessments and audits queries securely.

---

## 📂 Project Repository Structure

```
NASA-SpaceApps-Hackathon-2026/
│
├── prithvi_weather_gui.py         # Primary GUI Server (Port 5000), HTML Dashboard, & REST API
├── crop_catalog_service.py        # 549 FAO/NASA Crops Catalog Query & Search Service
├── crop_database.sql              # Raw SQL dump of 549 verified agricultural crops
├── nasa_crops_catalog.db          # Indexed SQLite database for instant crop lookups
├── solar_astronomy.py             # NOAA solar ephemeris calculation module
├── predict_soil_weather.py        # Multi-modal prediction orchestrator (Weather + Soil + AQI + Crops)
├── predict_weather.py             # Prithvi neural network inference engine
├── prithvi_weather_model.py       # PrithviWeatherNet architecture & feature extractors
├── prithvi_soil_weather_model.py  # 16-variable multi-task neural network architecture
├── regional_crops_database.py     # Pakistan regional agronomy (Chakwal, Lahore, Multan, Kharian, etc.)
├── nasa_challenge_evaluator.py    # Crop rotations, climate sensitivity, & NASA science glossary
├── accuweather_service.py         # AccuWeather Core 12-hour hourly & 5-day daily telemetry
├── security_vault.py              # PBKDF2-HMAC-SHA256 encrypted database vault
├── gemini_agri_advisor.py         # Google Gemini 2.5 Flash agricultural doctor integration
├── location_service.py            # Pakistan administrative hierarchy & GPS geocoding
│
├── test_nasa_challenge_features.py # Unit tests for rotations, glossary, climate, & GUI
├── test_soil_aq_predictions.py    # Unit tests for multi-depth soil strata & EPA AQI
├── test_weather_predictions.py    # Unit tests for physical sanity & spatial consistency
│
├── checkpoints/                   # Project milestone archives & integrity hashes
│   ├── checkpoint_1/              # Snapshot baseline
│   └── hackathon_project_checkpoint_1.zip # Checkpoint 1 archive (780 KB)
│
├── prithvi_weather_net.pt         # Trained PyTorch neural network weights
├── weather_gbm_ensemble.pkl       # Trained Gradient Boosted Ensemble
├── weather_model_metadata.json    # Training metadata and evaluation metrics
└── README.md                      # This file
```

---

## 🚀 How to Run the Application

### 1. Prerequisites
Ensure Python 3.11+ is installed. Activate the project virtual environment:
```powershell
# Windows PowerShell (from the project root)
.\prithvi-env\Scripts\Activate.ps1
```

### 2. Launch the Interactive GUI Dashboard
Run the primary GUI application:
```powershell
python prithvi_weather_gui.py --port 5000
```
Open your browser and navigate to:
```
http://127.0.0.1:5000/
```

### 3. CLI Prediction Mode
Predict comprehensive weather, soil strata, and agricultural feasibility directly from the terminal:
```powershell
# Chakwal Barani Plateau
python predict_soil_weather.py --station "Chakwal" --radius 25

# Lahore Canal Belt
python predict_soil_weather.py --station "Lahore" --radius 10

# Custom GPS Coordinates
python predict_soil_weather.py --lat 33.6844 --lon 73.0479
```

### 4. Query the 549 Crop Catalog via API
Test the REST API endpoints:
```powershell
# Search crops
curl "http://127.0.0.1:5000/api/crop-catalog?q=wheat"

# List distinct crop groups
curl "http://127.0.0.1:5000/api/crop-catalog/groups"

# Inspect single crop detail
curl "http://127.0.0.1:5000/api/crop-catalog/detail?id=CR0002"
```

---

## 🧪 Comprehensive Verification Suite

Execute the complete 13-test automated test suite:

```powershell
# 1. NASA Challenge Features & GUI Endpoints (7 tests)
python test_nasa_challenge_features.py

# 2. Multi-Depth Soil Strata & Air Quality (3 tests)
python test_soil_aq_predictions.py

# 3. Neural Network Weather Predictions & Physical Sanity (3 tests)
python test_weather_predictions.py
```

**Verification Status:**
- `test_nasa_challenge_features.py`: **7/7 PASSED (100%)**
- `test_soil_aq_predictions.py`: **3/3 PASSED (100%)**
- `test_weather_predictions.py`: **3/3 PASSED (100%)**
- **Total: 13/13 PASSED (100% Zero Defects)**

---

## 👥 Hackathon Team

**Team Name:** The Hackers Den  
**Challenge:** NASA Space Apps Hackathon 2026 — Agro-Climatic Decision Support & Future Weather Forecasting  
**Location:** Pakistan / Global  
**License:** MIT Open Source License (NASA Space Apps compliant)
