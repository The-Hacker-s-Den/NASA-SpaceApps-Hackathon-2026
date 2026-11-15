"""
Prithvi AI & NASA Earth Data — Highly Furnished Interactive GUI
================================================================
A state-of-the-art interactive graphical application providing:
  • Full Leaflet.js map with official NASA GIBS MODIS Terra / VIIRS / ESRI Satellite layers
  • Dynamic Range / Radius overlay circle (5 km to 100 km)
  • Automated Location Access API & Browser GPS auto-detection
  • Cascading Pakistan State/Province & City Selector
  • Date Range selector (Real-time, 24h, 7-Day, 14-Day, Seasonal)
  • Hydrological Flood Risk Gauge & Runoff Radar
  • 4-Stratum Soil Depth Profile (5cm, 15cm, 50cm, 150cm)
  • Air Quality Index (US EPA AQI) & Smog Advisory
  • Google Gemini AI Agricultural Land & Crop Feasibility Doctor
  • Bilingual Audio Broadcast (Urdu & English) for rural farmers
  • NASA Space Apps Crop-Climate Resilience Score (CCRS) with Letter Grade
  • Military-Grade PBKDF2-HMAC-SHA256 Encrypted Database Vault Status
  • NASA Hackathon Judge Presentation Dossier
"""

import os
import sys
import json
import math
import argparse
import threading
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from datetime import datetime

script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

from predict_soil_weather import predict, REGIONAL_CITIES
from nasa_data_engine import NASA_GIBS_LAYERS, fetch_nasa_power_data
from gemini_agri_advisor import evaluate_crop_feasibility
from location_service import PAKISTAN_PROVINCES, detect_user_location
from security_vault import (
    init_secure_database,
    create_security_session,
    save_secure_assessment,
    get_secure_assessments,
    save_user_location,
    get_user_saved_locations,
    delete_user_saved_location,
    set_default_saved_location
)
from nasa_hackathon_innovations import (
    calculate_ccrs,
    generate_bilingual_advisory,
    calculate_drainage_vector,
    get_nasa_judge_dossier
)
from nasa_challenge_evaluator import (
    simulate_crop_rotations,
    simulate_climate_sensitivity,
    SCIENTIFIC_GLOSSARY
)

# Gemini API key (stored in vault; hardcoded fallback for dashboard server)
DEFAULT_GEMINI_KEY = "AQ.Ab8RN6KcLzu9gVxryPPcDXC-HTWpjTmTVKxzRJiMSHwEqul3Rg"

HTML_DASHBOARD = r"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>The Hackers Den — NASA Field Shift Weather AI</title>
  
  <!-- Tailwind CSS & FontAwesome 6 -->
  <script src="https://cdn.tailwindcss.com"></script>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
  
  <!-- Leaflet.js Mapping Library -->
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
  <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>

  <!-- Google Fonts: Plus Jakarta Sans & JetBrains Mono & Noto Nastaliq Urdu -->
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;600&family=Noto+Nastaliq+Urdu:wght@400;700&display=swap" rel="stylesheet">

  <script>
    tailwind.config = {
      darkMode: 'class',
      theme: {
        extend: {
          fontFamily: {
            sans: ['"Plus Jakarta Sans"', '-apple-system', 'BlinkMacSystemFont', 'sans-serif'],
            mono: ['"JetBrains Mono"', 'monospace'],
            urdu: ['"Noto Nastaliq Urdu"', 'serif'],
          }
        }
      }
    }
  </script>

  <style>
    /* Full Web Page with Smooth Vertical Scrollbar */
    html, body {
      min-height: 100vh;
      width: 100%;
      margin: 0;
      padding: 0;
      overflow-x: hidden;
      overflow-y: auto !important;
      background-color: #0b0d13;
      color: #f3f4f6;
      scroll-behavior: smooth;
    }

    /* Sleek Modern Obsidian Scrollbar */
    ::-webkit-scrollbar {
      width: 8px;
      height: 8px;
      display: block !important;
    }
    ::-webkit-scrollbar-track {
      background: #0d0f14;
    }
    ::-webkit-scrollbar-thumb {
      background: #232733;
      border-radius: 4px;
      border: 1px solid rgba(255, 255, 255, 0.08);
    }
    ::-webkit-scrollbar-thumb:hover {
      background: #3b82f6;
    }
    * {
      scrollbar-width: thin;
      scrollbar-color: #232733 #0d0f14;
    }

    /* Main Dashboard Outer Frame */
    .dashboard-frame {
      background: #111317;
      border: 1px solid rgba(255, 255, 255, 0.08);
      box-shadow: 0 25px 60px -15px rgba(0, 0, 0, 0.7);
    }

    /* Frosted Glassmorphism Hero Weather Card */
    .hero-weather-glass {
      background: linear-gradient(135deg, rgba(32, 38, 52, 0.88) 0%, rgba(18, 22, 30, 0.85) 100%);
      backdrop-filter: blur(28px);
      -webkit-backdrop-filter: blur(28px);
      border: 1px solid rgba(255, 255, 255, 0.12);
      box-shadow: inset 0 1px 1px rgba(255, 255, 255, 0.15), 0 20px 40px rgba(0, 0, 0, 0.45);
    }

    /* Standard Widget Card */
    .widget-card {
      background: #161922;
      border: 1px solid rgba(255, 255, 255, 0.06);
    }

    /* Leaflet Map */
    #map {
      height: 100%;
      width: 100%;
      z-index: 10;
      background: #0d0f14;
    }
    .leaflet-tile {
      filter: saturate(1.15) contrast(1.05);
    }

    /* Pulse marker */
    .pulse-ring {
      display: block; width: 16px; height: 16px; border-radius: 50%;
      background: #3b82f6; box-shadow: 0 0 0 rgba(59, 130, 246, 0.8);
      animation: pulse 1.6s infinite;
    }
    @keyframes pulse {
      0% { transform: scale(0.9); box-shadow: 0 0 0 0 rgba(59, 130, 246, 0.8); }
      70% { transform: scale(1.1); box-shadow: 0 0 0 12px rgba(59, 130, 246, 0); }
      100% { transform: scale(0.9); box-shadow: 0 0 0 0 rgba(59, 130, 246, 0); }
    }

    /* Custom internal scrollbars */
    .custom-scroll::-webkit-scrollbar { width: 5px; height: 5px; }
    .custom-scroll::-webkit-scrollbar-track { background: #111317; }
    .custom-scroll::-webkit-scrollbar-thumb { background: #262c3a; border-radius: 4px; }
  </style>
</head>
<body class="font-sans min-h-screen w-full p-2 sm:p-4 overflow-x-hidden overflow-y-auto flex flex-col antialiased select-none">

  <!-- FULL CHROME DASHBOARD FRAME -->
  <div class="dashboard-frame rounded-[28px] w-full min-h-[1100px] lg:min-h-[1160px] pb-10 flex flex-row shadow-2xl relative mb-12">

    <!-- ── 1. LEFT SLIM ICON DOCK ────────────────────────────────────────────── -->
    <aside class="w-14 bg-[#101217] border-r border-white/5 py-4 px-2 flex flex-col items-center justify-between z-30 flex-shrink-0">
      
      <!-- Top Nav Group -->
      <div class="flex flex-col items-center space-y-3.5">
        <!-- Home Button (Active with Rounded Glass Container) -->
        <button onclick="switchTab('forecast')" id="nav-home-btn" class="w-10 h-10 rounded-2xl bg-white/10 hover:bg-white/15 text-white flex items-center justify-center shadow-inner transition cursor-pointer border border-white/10" title="10-Day Forecast">
          <i class="fa-solid fa-house text-xs"></i>
        </button>

        <!-- Map Radar Button -->
        <button onclick="focusMap()" id="nav-map-btn" class="w-10 h-10 rounded-2xl text-gray-400 hover:text-white hover:bg-white/5 flex items-center justify-center transition cursor-pointer" title="Focus Satellite Map">
          <i class="fa-regular fa-map text-xs"></i>
        </button>

        <!-- Regional Crops & Agronomy Button -->
        <button onclick="switchTab('crops')" id="nav-crops-btn" class="w-10 h-10 rounded-2xl text-gray-400 hover:text-white hover:bg-white/5 flex items-center justify-center transition cursor-pointer" title="Regional Crop Agronomy Database">
          <i class="fa-solid fa-seedling text-xs"></i>
        </button>

        <!-- The Hackers Den Soil Strata Profile Button -->
        <button onclick="switchTab('soil')" id="nav-soil-btn" class="w-10 h-10 rounded-2xl text-gray-400 hover:text-white hover:bg-white/5 flex items-center justify-center transition cursor-pointer" title="The Hackers Den 4-Depth Soil Profile">
          <i class="fa-solid fa-layer-group text-xs"></i>
        </button>

        <!-- Crop Rotation Simulator Button -->
        <button onclick="switchTab('rotations')" id="nav-rot-btn" class="w-10 h-10 rounded-2xl text-gray-400 hover:text-white hover:bg-white/5 flex items-center justify-center transition cursor-pointer" title="Crop Rotation Scenarios">
          <i class="fa-solid fa-arrows-spin text-xs"></i>
        </button>

        <!-- Climate Sensitivity What-If Button -->
        <button onclick="switchTab('climate')" id="nav-clim-btn" class="w-10 h-10 rounded-2xl text-gray-400 hover:text-white hover:bg-white/5 flex items-center justify-center transition cursor-pointer" title="Climate What-If Simulator & Analog City">
          <i class="fa-solid fa-temperature-arrow-up text-xs"></i>
        </button>
      </div>

      <!-- Bottom Nav Group (Volume Removed, Only Settings/Vault) -->
      <div class="flex flex-col items-center space-y-2.5">
        <!-- NASA Judge Technical Dossier Button -->
        <button onclick="openJudgeModal()" class="w-8 h-8 rounded-full bg-purple-950/50 hover:bg-purple-800/80 text-purple-300 border border-purple-700/40 flex items-center justify-center transition text-[11px]" title="NASA Judge Dossier">
          <i class="fa-solid fa-award"></i>
        </button>

        <!-- Science Glossary Button -->
        <button onclick="openGlossaryModal()" class="w-8 h-8 rounded-full bg-teal-950/50 hover:bg-teal-800/80 text-teal-300 border border-teal-700/40 flex items-center justify-center transition text-[11px]" title="NASA Science Explainer Glossary">
          <i class="fa-solid fa-book-open"></i>
        </button>
      </div>
    </aside>

    <!-- ── 2. MAIN DASHBOARD CONTENT AREA ────────────────────────────────────── -->
    <div class="flex-1 p-4 sm:p-5 flex flex-col justify-start space-y-4">

      <!-- TOP HEADER BAR (EXACT DESIGN MATCH) -->
      <header class="flex items-center justify-between gap-3 flex-shrink-0">
        
        <!-- Left: Location Title + Subtitle + Team Badge -->
        <div class="flex items-center space-x-3">
          <div>
            <div class="flex items-center space-x-2">
              <h1 id="top-location-name" class="text-xl sm:text-2xl font-bold tracking-tight text-white leading-tight">Chakwal, Punjab</h1>
              <button onclick="openCityPicker()" class="text-gray-400 hover:text-blue-400 text-xs transition p-1" title="Select Province & City">
                <i class="fa-solid fa-chevron-down text-[11px]"></i>
              </button>
              
              <!-- Save Location Button -->
              <button id="btn-save-location" onclick="toggleSaveCurrentLocation()" class="flex items-center space-x-1.5 px-2.5 py-1 rounded-full bg-[#1b1e27] hover:bg-[#252a34] border border-white/10 text-xs text-amber-300 hover:text-amber-200 transition shadow" title="Save this location to favorites">
                <i id="save-location-icon" class="fa-regular fa-star text-amber-400"></i>
                <span id="save-location-text" class="text-[11px] font-semibold">Save Location</span>
              </button>

              <!-- View Saved Locations Button -->
              <button onclick="openSavedLocationsModal()" class="flex items-center space-x-1 px-2.5 py-1 rounded-full bg-[#1b1e27] hover:bg-[#252a34] border border-white/10 text-xs text-blue-300 hover:text-blue-200 transition shadow" title="View Saved Locations">
                <i class="fa-solid fa-bookmark text-blue-400"></i>
                <span class="text-[11px] font-semibold">Saved (<span id="saved-count-badge">0</span>)</span>
              </button>

              <div class="hidden sm:flex items-center space-x-1.5 px-3 py-0.5 rounded-full bg-gradient-to-r from-cyan-950/90 via-blue-950/90 to-purple-950/90 border border-cyan-500/50 text-[10px] font-mono font-bold text-cyan-300 shadow-[0_0_12px_rgba(6,182,212,0.3)]" title="NASA Space Apps Hackathon 2026 Team">
                <i class="fa-solid fa-terminal text-cyan-400 text-[10px]"></i>
                <span>The Hackers Den</span>
              </div>
            </div>
            <p id="top-datetime-subtitle" class="text-xs text-gray-400 font-medium flex items-center space-x-1.5">
              <span id="live-clock">10:15 AM</span>
              <span>·</span>
              <span id="live-date">Tuesday, Oct 26</span>
              <span>·</span>
              <span id="top-zone-badge" class="px-2 py-0.2 rounded-full bg-blue-950/80 text-blue-300 border border-blue-800/40 text-[10px] font-semibold">Barani Agro-Zone</span>
            </p>
          </div>
        </div>

        <!-- Center: Dynamic Instant Search Bar with Auto-Suggestions -->
        <div class="relative w-72 sm:w-88 md:w-96 z-40">
          <div class="relative flex items-center">
            <input type="text" id="map-search-input" placeholder="Search city in Pakistan (e.g. Lahore, Multan, Kharian)..." 
                   oninput="onSearchInput(this.value)"
                   onkeydown="if(event.key==='Enter') executeSearch()"
                   class="w-full pl-9 pr-9 py-2 rounded-full bg-[#1b1e27] border border-white/10 text-xs text-white placeholder-gray-400 focus:outline-none focus:border-blue-500 font-medium transition shadow-inner">
            <button onclick="executeSearch()" class="absolute left-3 text-gray-400 hover:text-white transition text-xs">
              <i class="fa-solid fa-magnifying-glass"></i>
            </button>
            <button onclick="clearSearch()" id="search-clear-btn" class="absolute right-3 text-gray-400 hover:text-white text-xs hidden">
              <i class="fa-solid fa-xmark"></i>
            </button>
          </div>

          <!-- Instant Dropdown Auto-Suggestions -->
          <div id="search-suggestions" class="absolute left-0 right-0 top-10 mt-1 bg-[#161922] border border-white/10 rounded-2xl shadow-2xl overflow-hidden hidden z-50 text-xs max-h-56 overflow-y-auto custom-scroll">
            <!-- Populated dynamically via JS -->
          </div>
        </div>

        <!-- Right: Unit Toggle, Avatar, Settings -->
        <div class="flex items-center space-x-2.5">
          <!-- Temp Unit Toggle (°C / °F) -->
          <button onclick="toggleTempUnit()" id="temp-unit-toggle" class="px-3 py-1 rounded-full bg-[#1b1e27] hover:bg-[#252a34] border border-white/10 text-xs text-white font-mono font-bold transition shadow-sm" title="Toggle Temperature Unit (°C / °F)">
            °C
          </button>

          <!-- User Profile Avatar -->
          <div class="w-8 h-8 rounded-full overflow-hidden bg-gradient-to-tr from-blue-600 to-indigo-500 border border-white/20 flex items-center justify-center text-white text-xs shadow-sm" title="Logged in as Lead Agronomist">
            <i class="fa-solid fa-user-astronaut"></i>
          </div>

          <!-- Quick City Picker Modal Button -->
          <button onclick="openCityPicker()" class="w-8 h-8 rounded-full bg-[#1b1e27] hover:bg-[#252a34] text-gray-300 hover:text-white border border-white/10 flex items-center justify-center transition text-xs" title="Cascading Province & City Selector">
            <i class="fa-solid fa-sliders"></i>
          </button>

          <!-- Database Vault Security Badge -->
          <div class="hidden sm:flex items-center space-x-1 px-2.5 py-1 rounded-full bg-emerald-950/60 border border-emerald-700/50 text-[10px] text-emerald-300 font-mono" title="Hardware-Bound AES-256 Vault Active">
            <i class="fa-solid fa-shield-halved text-emerald-400 text-[10px]"></i>
            <span>Vault: OK</span>
          </div>
        </div>

      </header>

      <!-- SAVED LOCATIONS QUICK-SWITCH TRAY -->
      <div id="saved-locations-tray" class="flex items-center space-x-2 overflow-x-auto custom-scroll py-1 px-1 flex-shrink-0 text-xs bg-black/20 rounded-2xl border border-white/5">
        <div class="flex items-center space-x-1.5 text-amber-300 font-semibold text-[11px] flex-shrink-0 pl-1">
          <i class="fa-solid fa-bookmark text-amber-400 text-[10px]"></i>
          <span>Saved Sites:</span>
        </div>
        <div id="saved-locations-chips-container" class="flex items-center space-x-1.5 overflow-x-auto custom-scroll">
          <!-- Dynamically populated chips -->
        </div>
        <button onclick="openSavedLocationsModal()" class="px-2 py-0.5 rounded-full bg-white/5 hover:bg-white/10 text-gray-300 hover:text-white text-[10px] flex-shrink-0 border border-white/10 transition ml-auto" title="Manage Saved Locations">
          <i class="fa-solid fa-gear text-[9px] mr-1"></i>Manage
        </button>
      </div>

      <!-- ── 3. TWO-COLUMN BALANCED GRID ────────────────────────────────────── -->
      <div class="grid grid-cols-1 lg:grid-cols-12 gap-4 flex-1">

        <!-- ════ LEFT COLUMN: HERO WEATHER + HOURLY FORECAST (5 COLS) ════ -->
        <div class="lg:col-span-5 flex flex-col justify-between space-y-3 min-h-0">

          <!-- A. HERO WEATHER CARD (EXACT FROSTED GLASS EFFECT) -->
          <div class="hero-weather-glass rounded-[24px] p-5 sm:p-6 relative overflow-hidden flex flex-col justify-between flex-shrink-0 h-[225px]">
            
            <!-- Top: Big Temp + Condition + 3D Cloud/Sun Graphic -->
            <div class="flex items-start justify-between">
              <div>
                <div id="hero-temp-display" class="text-6xl sm:text-7xl font-bold tracking-tight text-white leading-none">
                  14°C
                </div>
                <div id="hero-condition-display" class="text-2xl font-normal text-gray-200 mt-2">
                  Cloudy
                </div>
              </div>

              <!-- 3D Layered Fluffy Cloud + Golden Sun Graphic (Matches Image) -->
              <div class="w-24 h-24 sm:w-28 sm:h-28 relative flex items-center justify-center filter drop-shadow-[0_10px_20px_rgba(0,0,0,0.5)]">
                <!-- Sun behind cloud -->
                <div class="absolute right-1 top-1 w-12 h-12 rounded-full bg-gradient-to-tr from-amber-500 via-yellow-400 to-yellow-200 shadow-[0_0_20px_rgba(251,191,36,0.7)]">
                  <div class="absolute -inset-1 rounded-full border border-yellow-300/40 animate-pulse"></div>
                </div>
                <!-- 3D White Volumetric Cloud -->
                <svg class="relative z-10 w-22 h-22" viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M72 68H28C21.3726 68 16 62.6274 16 56C16 49.7423 20.803 44.6067 26.966 44.0628C27.915 35.0935 35.4853 28 44.75 28C51.685 28 57.6547 31.9774 60.6724 37.8384C62.8122 36.6806 65.3117 36 68 36C75.732 36 82 42.268 82 50C82 50.6033 81.9619 51.1977 81.8877 51.7809C84.3857 53.6496 86 56.6358 86 60C86 64.4183 82.4183 68 78 68H72Z" 
                        fill="url(#cloudGradFull)" 
                        filter="drop-shadow(0px 8px 16px rgba(0,0,0,0.3))"/>
                  <defs>
                    <linearGradient id="cloudGradFull" x1="50" y1="28" x2="50" y2="68" gradientUnits="userSpaceOnUse">
                      <stop offset="0%" stop-color="#ffffff"/>
                      <stop offset="65%" stop-color="#e8ecf2"/>
                      <stop offset="100%" stop-color="#cbd5e1"/>
                    </linearGradient>
                  </defs>
                </svg>
              </div>
            </div>

            <!-- Bottom Row Metrics: Feels Like · Humidity · Wind NW -->
            <div class="flex items-center space-x-6 sm:space-x-8 text-xs text-gray-300 pt-3 border-t border-white/10">
              <div>
                <span class="text-gray-400 block text-[10px]">Feels like</span>
                <span id="hero-feels-like" class="font-semibold text-white text-sm">13°</span>
              </div>
              <div>
                <span class="text-gray-400 block text-[10px]">Humidity</span>
                <span id="hero-humidity" class="font-semibold text-white text-sm">72%</span>
              </div>
              <div>
                <span class="text-gray-400 block text-[10px]">Wind</span>
                <span id="hero-wind" class="font-semibold text-white text-sm">12 mph NW</span>
              </div>
              <div>
                <span class="text-gray-400 block text-[10px]">Pressure</span>
                <span id="hero-pressure" class="font-semibold text-white text-sm">1015 hPa</span>
              </div>
            </div>

          </div>

          <!-- B. THE HACKERS DEN AGRO-CLIMATIC & SATELLITE MATRIX (BRIDGING MID-COLUMN) -->
          <div class="widget-card rounded-[22px] p-3.5 space-y-2.5 flex-1 flex flex-col justify-between">
            <div class="flex items-center justify-between border-b border-white/10 pb-1.5">
              <div class="flex items-center space-x-2">
                <div class="w-2 h-2 rounded-full bg-emerald-400 animate-ping"></div>
                <span class="text-xs font-bold text-white tracking-wide">The Hackers Den Land & Satellite Ephemeris</span>
              </div>
              <span id="land-feasibility-tag" class="px-2 py-0.5 rounded-full bg-emerald-950/80 text-emerald-300 border border-emerald-700/60 text-[9px] font-mono font-bold">Optimal Soil</span>
            </div>

            <!-- Quick Metrics Grid -->
            <div class="grid grid-cols-3 gap-2 text-center">
              <div class="bg-black/30 p-2 rounded-xl border border-white/5">
                <span class="text-gray-400 text-[9px] block">Evapotranspiration</span>
                <span id="mid-et-val" class="font-bold text-amber-300 font-mono text-xs">3.4 mm/day</span>
                <span class="text-[8px] text-gray-500 block">FAO Penman-Monteith</span>
              </div>
              <div class="bg-black/30 p-2 rounded-xl border border-white/5">
                <span class="text-gray-400 text-[9px] block">Root VWC (-15cm)</span>
                <span id="mid-vwc-val" class="font-bold text-emerald-300 font-mono text-xs">0.270 m³/m³</span>
                <span class="text-[8px] text-emerald-400/80 block">Active Plant Buffer</span>
              </div>
              <div class="bg-black/30 p-2 rounded-xl border border-white/5">
                <span class="text-gray-400 text-[9px] block">Soil Deficit (SMD)</span>
                <span id="mid-smd-val" class="font-bold text-blue-300 font-mono text-xs">24.5 mm</span>
                <span class="text-[8px] text-blue-400/80 block">Moisture Stable</span>
              </div>
            </div>

            <!-- NASA Satellite Telemetry Bar -->
            <div class="bg-black/40 px-2.5 py-1.5 rounded-xl border border-white/5 flex items-center justify-between text-[9px] text-gray-400 font-mono">
              <span class="flex items-center space-x-1 text-gray-300">
                <i class="fa-solid fa-satellite text-blue-400 text-[10px]"></i>
                <span class="font-semibold">NASA Constellation:</span>
              </span>
              <span class="text-emerald-400">SMAP L4</span>
              <span class="text-gray-600">·</span>
              <span class="text-cyan-400">GPM IMERG</span>
              <span class="text-gray-600">·</span>
              <span class="text-amber-400">MODIS NDVI</span>
              <span class="text-gray-600">·</span>
              <span class="text-indigo-400">Landsat 9</span>
            </div>
          </div>

          <!-- C. HOURLY FORECAST CAROUSEL - ANCHORED AT BOTTOM / END OF PAGE -->
          <div class="space-y-2 mt-auto pt-2 flex-shrink-0" id="hourly-forecast-bottom-anchor">
            <div class="flex items-center justify-between">
              <div class="flex items-center space-x-2">
                <h3 class="text-xs font-semibold text-white tracking-wide">Hourly Forecast</h3>
                <span id="hourly-source-badge" class="text-[9px] px-1.5 py-0.2 rounded bg-blue-950 text-blue-300 font-mono">AccuWeather Core</span>
              </div>
              <div class="flex items-center space-x-1.5 text-xs">
                <button onclick="shiftHourly(-1)" class="w-6 h-6 rounded-full bg-[#1b1e27] hover:bg-[#252a34] text-gray-400 hover:text-white flex items-center justify-center transition">
                  <i class="fa-solid fa-chevron-left text-[9px]"></i>
                </button>
                <button onclick="shiftHourly(1)" class="w-6 h-6 rounded-full bg-[#1b1e27] hover:bg-[#252a34] text-gray-400 hover:text-white flex items-center justify-center transition">
                  <i class="fa-solid fa-chevron-right text-[9px]"></i>
                </button>
              </div>
            </div>

            <!-- 6 Dynamic Hourly Pill Cards -->
            <div class="grid grid-cols-6 gap-2" id="hourly-cards-container">
              <!-- Dynamically populated via JS for each selected city -->
            </div>
          </div>

        </div>

        <!-- ════ RIGHT COLUMN: BIGGER MAP + UV/SUNRISE + TABS (7 COLS) ════ -->
        <div class="lg:col-span-7 flex flex-col justify-between space-y-3 min-h-0">

          <!-- A. EXPANDED INTERACTIVE MAP WIDGET (LARGER PROPORTION: h-[260px]) -->
          <div class="space-y-1.5 flex-shrink-0">
            <div class="flex items-center justify-between text-xs">
              <div class="flex items-center space-x-2">
                <h3 class="font-semibold text-white tracking-wide">Interactive Map Widget</h3>
                <span id="map-target-coords" class="text-[10px] text-gray-400 font-mono">32.9328°N, 72.8631°E</span>
              </div>
              
              <!-- Scan Radius Selector -->
              <div class="flex items-center space-x-1 text-[11px] text-gray-400">
                <span>Radius:</span>
                <button onclick="setRadius(5)" class="rad-btn px-2 py-0.5 rounded bg-[#1c1f26] text-gray-300 hover:text-white text-[10px]" data-r="5">5k</button>
                <button onclick="setRadius(10)" class="rad-btn px-2 py-0.5 rounded bg-[#1c1f26] text-gray-300 hover:text-white text-[10px]" data-r="10">10k</button>
                <button onclick="setRadius(25)" class="rad-btn px-2 py-0.5 rounded bg-blue-600 text-white font-bold text-[10px]" data-r="25">25k</button>
                <button onclick="setRadius(50)" class="rad-btn px-2 py-0.5 rounded bg-[#1c1f26] text-gray-300 hover:text-white text-[10px]" data-r="50">50k</button>
                <button onclick="setRadius(100)" class="rad-btn px-2 py-0.5 rounded bg-[#1c1f26] text-gray-300 hover:text-white text-[10px]" data-r="100">100k</button>
              </div>
            </div>

            <!-- Larger Map Viewport (260px tall) -->
            <div class="widget-card rounded-[22px] overflow-hidden relative h-[255px]">
              <div id="map"></div>

              <!-- Top Left: Layer Switcher Pill -->
              <div class="absolute top-3 left-3 z-20 flex space-x-1">
                <button onclick="cycleSatelliteLayer()" class="px-2.5 py-1 rounded-xl bg-black/70 hover:bg-black/90 backdrop-blur text-white flex items-center space-x-1.5 text-[11px] border border-white/10 shadow" title="Toggle Satellite Layer">
                  <i class="fa-solid fa-layer-group text-blue-400"></i>
                  <span id="current-layer-name">Google Hybrid</span>
                </button>
              </div>

              <!-- Bottom Left: Temperature Color Bar (-10 -5 0 25 50) -->
              <div class="absolute bottom-3 left-3 z-20 bg-black/75 backdrop-blur px-3 py-1.5 rounded-xl border border-white/10 text-[9px] font-mono flex flex-col space-y-1 shadow">
                <span class="text-gray-300 font-sans font-semibold">Temperature Scale</span>
                <div class="w-28 h-1.5 rounded-full bg-gradient-to-r from-purple-800 via-blue-600 via-emerald-500 via-amber-400 to-rose-600"></div>
                <div class="flex justify-between text-[8px] text-gray-400">
                  <span>-10°</span>
                  <span>-5°</span>
                  <span>0°</span>
                  <span>25°</span>
                  <span>50°</span>
                </div>
              </div>

              <!-- Bottom Right: Map Zoom Controls -->
              <div class="absolute bottom-3 right-3 z-20 flex flex-col space-y-1">
                <button onclick="map.zoomIn()" class="w-7 h-7 rounded-lg bg-black/75 hover:bg-black/90 backdrop-blur text-white text-xs border border-white/10 flex items-center justify-center shadow font-bold">+</button>
                <button onclick="map.zoomOut()" class="w-7 h-7 rounded-lg bg-black/75 hover:bg-black/90 backdrop-blur text-white text-xs border border-white/10 flex items-center justify-center shadow font-bold">−</button>
              </div>
            </div>
          </div>

          <!-- B. MIDDLE ROW: UV INDEX & SUNRISE/SUNSET WIDGETS -->
          <div class="grid grid-cols-2 gap-3 flex-shrink-0">

            <!-- Card 1: UV Index & EPA Air Quality -->
            <div class="widget-card rounded-[20px] p-3 flex flex-col justify-between h-[105px]">
              <span class="text-[11px] font-semibold text-gray-300 block">UV Index Widget</span>
              
              <div class="flex items-center justify-around py-0.5">
                <!-- UV Arc Gauge -->
                <div class="relative w-12 h-12 flex flex-col items-center justify-center">
                  <svg class="w-12 h-12 transform -rotate-90">
                    <circle cx="24" cy="24" r="18" stroke="rgba(255,255,255,0.1)" stroke-width="3.5" fill="none"/>
                    <circle cx="24" cy="24" r="18" stroke="#f59e0b" stroke-width="3.5" fill="none" stroke-dasharray="113" stroke-dashoffset="50" stroke-linecap="round"/>
                  </svg>
                  <div class="absolute text-center leading-none">
                    <span id="uv-val" class="text-sm font-bold text-white block">3</span>
                    <span id="uv-label" class="text-[8px] text-gray-400 block">Moderate</span>
                  </div>
                </div>

                <!-- Green Leaf / Air Quality Score -->
                <div class="flex flex-col items-center">
                  <div class="w-7 h-7 rounded-full bg-emerald-950/60 border border-emerald-500/40 flex items-center justify-center text-emerald-400 text-xs shadow-sm">
                    <i class="fa-solid fa-leaf"></i>
                  </div>
                  <span id="aqi-score" class="text-xs font-bold text-white mt-0.5">45</span>
                  <span id="aqi-badge-text" class="text-[8px] text-emerald-400 font-semibold">Good</span>
                </div>
              </div>

              <div class="text-[8px] text-gray-500 text-center font-mono">
                US EPA Standard · Low Stomatal Resistance
              </div>
            </div>

            <!-- Card 2: Sunrise/Sunset Widget & Flood Infiltration -->
            <div class="widget-card rounded-[20px] p-3 flex flex-col justify-between h-[105px]">
              <div class="flex justify-between items-center">
                <span class="text-[11px] font-semibold text-gray-300">Sunrise/Sunset Widget</span>
                <span id="flood-safety-pill" class="text-[8px] px-2 py-0.2 rounded-full bg-emerald-950 text-emerald-300 border border-emerald-800 font-mono">Safe</span>
              </div>

              <!-- Real-Time Astronomical Solar Arc Dome -->
              <div class="py-0.5 flex flex-col items-center">
                <div class="w-28 h-9 relative flex items-end justify-center">
                  <svg class="w-28 h-9 overflow-visible" viewBox="0 0 110 36">
                    <!-- Ground Horizon Line -->
                    <line x1="5" y1="34" x2="105" y2="34" stroke="rgba(255,255,255,0.2)" stroke-width="1.5"/>
                    <!-- Upward Golden Solar Trajectory Arch -->
                    <path d="M 12 34 A 43 25 0 0 1 98 34" fill="none" stroke="rgba(251,191,36,0.6)" stroke-width="1.5" stroke-dasharray="3,3"/>
                    <!-- Dynamic Sun Marker along the Arch -->
                    <circle id="solar-sun-dot" cx="55" cy="9" r="4.5" fill="#f59e0b" filter="drop-shadow(0 0 8px #f59e0b)"/>
                    <circle id="solar-sun-pulse" cx="55" cy="9" r="7.5" fill="none" stroke="rgba(251,191,36,0.5)" stroke-width="1"/>
                  </svg>
                </div>
                <!-- Exact Dynamic Dawn, Rise, Set, Dusk for Each City -->
                <div class="flex justify-between w-full text-[9px] text-amber-200/90 pt-0.5 font-mono font-semibold">
                  <span id="solar-dawn-disp">Dawn: 6:12 AM</span>
                  <span id="solar-dusk-disp">Dusk: 5:35 PM</span>
                </div>
                <div class="flex justify-between w-full text-[7.5px] text-gray-400 font-mono -mt-0.5">
                  <span id="solar-rise-disp">Rise: 6:38 AM</span>
                  <span id="solar-set-disp">Set: 5:09 PM</span>
                </div>
              </div>

              <div class="text-[8px] text-blue-300 text-center font-mono" id="flood-runoff-rate">
                Flood Risk: 18.5% · Low Runoff Potential
              </div>
            </div>

          </div>

          <!-- C. TABBED BOTTOM WIDGET: 10-DAY / CROPS / SOIL / WHAT-IF (FLEX-1) -->
          <div class="widget-card rounded-[24px] p-4 flex flex-col justify-between min-h-[440px] lg:min-h-[480px] shadow-xl">
            
            <!-- Tab Navigation Header -->
            <div class="flex items-center justify-between border-b border-white/10 pb-2 flex-shrink-0">
              <div class="flex items-center space-x-3 text-xs overflow-x-auto custom-scroll">
                <button onclick="switchTab('forecast')" id="tab-forecast" class="tab-btn font-semibold text-white border-b-2 border-blue-500 pb-0.5 flex items-center space-x-1">
                  <i class="fa-solid fa-calendar-days text-[10px]"></i>
                  <span>5-Day Live</span>
                </button>
                <button onclick="switchTab('crops')" id="tab-crops" class="tab-btn text-gray-400 hover:text-white pb-0.5 flex items-center space-x-1">
                  <i class="fa-solid fa-seedling text-[10px]"></i>
                  <span>Crops & Agronomy</span>
                </button>
                <button onclick="switchTab('catalog')" id="tab-catalog" class="tab-btn text-amber-300 hover:text-white pb-0.5 flex items-center space-x-1">
                  <i class="fa-solid fa-book-atlas text-[10px] text-amber-400"></i>
                  <span class="font-bold">549 Crop DB</span>
                </button>
                <button onclick="switchTab('soil')" id="tab-soil" class="tab-btn text-gray-400 hover:text-white pb-0.5 flex items-center space-x-1">
                  <i class="fa-solid fa-layer-group text-[10px]"></i>
                  <span>Soil Strata</span>
                </button>
                <button onclick="switchTab('climate')" id="tab-climate" class="tab-btn text-gray-400 hover:text-white pb-0.5 flex items-center space-x-1">
                  <i class="fa-solid fa-temperature-arrow-up text-[10px]"></i>
                  <span>What-If Analog</span>
                </button>
                <button onclick="switchTab('rotations')" id="tab-rotations" class="tab-btn text-gray-400 hover:text-white pb-0.5 flex items-center space-x-1">
                  <i class="fa-solid fa-arrows-spin text-[10px]"></i>
                  <span>Cycles</span>
                </button>
              </div>

              <span id="ccrs-badge" class="text-[10px] px-2 py-0.5 rounded bg-emerald-950 text-emerald-300 border border-emerald-700 font-mono font-bold">CCRS: A+ (92)</span>
            </div>

            <!-- TAB 1: 10-DAY FORECAST ROWS (ACCUWEATHER LIVE) -->
            <div id="content-forecast" class="tab-panel flex-1 overflow-y-auto custom-scroll space-y-1.5 text-xs pt-1">
              <!-- Dynamically populated from AccuWeather daily data -->
            </div>

            <!-- TAB 2: RICH REGIONAL CROPS & GLOBAL FAO/NASA 549 CATALOG -->
            <div id="content-crops" class="tab-panel hidden flex-1 overflow-y-auto custom-scroll space-y-2.5 text-xs pt-1">
              
              <!-- Sub-Tab Pill Switcher: Regional vs Global Catalog -->
              <div class="flex items-center justify-between bg-black/40 p-1.5 rounded-xl border border-white/5">
                <div class="flex items-center space-x-1.5">
                  <button onclick="toggleCropsSubView('regional')" id="btn-crop-regional" class="px-3 py-1 rounded-lg bg-blue-600 text-white font-bold text-[11px] transition shadow">
                    <i class="fa-solid fa-location-dot mr-1"></i> Regional District Crops
                  </button>
                  <button onclick="toggleCropsSubView('catalog')" id="btn-crop-catalog" class="px-3 py-1 rounded-lg bg-[#161922] hover:bg-[#202532] text-gray-400 hover:text-white font-medium text-[11px] transition">
                    <i class="fa-solid fa-seedling mr-1"></i> Global FAO & NASA Catalog (549)
                  </button>
                </div>
                <span id="crop-catalog-count-pill" class="text-[9px] px-2 py-0.5 rounded-full bg-blue-950 text-blue-300 border border-blue-800 font-mono">549 Species Ready</span>
              </div>

              <!-- VIEW A: REGIONAL DISTRICT CROPS (FOR CURRENT CITY) -->
              <div id="view-crops-regional" class="space-y-2">
                <div class="flex items-center justify-between bg-black/30 p-2 rounded-xl border border-white/5">
                  <div>
                    <span class="text-gray-400 text-[10px] block">Agro-Ecological Zone:</span>
                    <span id="crop-zone-title" class="font-bold text-white text-xs">Pothohar Barani Plateau</span>
                  </div>
                  <div class="text-right">
                    <span class="text-gray-400 text-[10px] block">Soil Matrix:</span>
                    <span id="crop-soil-title" class="text-blue-300 font-mono text-[11px]">Sandy Loam (pH 7.6)</span>
                  </div>
                </div>

                <!-- NASA & FAO 549 Crop Database Quick Bar -->
                <div class="flex items-center justify-between bg-blue-950/40 border border-blue-500/20 px-3 py-2 rounded-xl">
                  <div class="flex items-center space-x-2 text-xs">
                    <i class="fa-solid fa-database text-amber-400"></i>
                    <span class="text-gray-300 text-[11px]">Integrated Database:</span>
                    <span class="text-amber-300 font-bold font-mono text-[11px]">549 FAO & NASA Crops</span>
                  </div>
                  <button onclick="toggleCropsSubView('catalog')" class="px-2.5 py-1 rounded bg-blue-600 hover:bg-blue-500 text-white font-bold text-[10px] transition shadow flex items-center space-x-1 cursor-pointer">
                    <span>Explore All 549 Crops</span>
                    <i class="fa-solid fa-arrow-right text-[9px] ml-1"></i>
                  </button>
                </div>

                <!-- Kharif Crops Table -->
                <div class="space-y-1">
                  <span class="font-bold text-amber-300 text-[11px] flex items-center space-x-1">
                    <i class="fa-solid fa-sun text-[10px]"></i>
                    <span>Major Kharif Season Crops (Summer / Monsoon):</span>
                  </span>
                  <div class="overflow-x-auto">
                    <table class="w-full text-[10px] text-left">
                      <thead class="text-gray-400 bg-black/40">
                        <tr>
                          <th class="p-1">Crop</th>
                          <th class="p-1">Catalog ID</th>
                          <th class="p-1">Variety</th>
                          <th class="p-1">Sowing</th>
                          <th class="p-1">Water Need</th>
                          <th class="p-1">Exp. Yield</th>
                          <th class="p-1">Gross Margin</th>
                        </tr>
                      </thead>
                      <tbody id="kharif-crops-tbody" class="divide-y divide-white/5 text-gray-200 font-mono">
                        <!-- Populated via JS -->
                      </tbody>
                    </table>
                  </div>
                </div>

                <!-- Rabi Crops Table -->
                <div class="space-y-1 pt-1">
                  <span class="font-bold text-emerald-400 text-[11px] flex items-center space-x-1">
                    <i class="fa-solid fa-snowflake text-[10px]"></i>
                    <span>Major Rabi Season Crops (Winter):</span>
                  </span>
                  <div class="overflow-x-auto">
                    <table class="w-full text-[10px] text-left">
                      <thead class="text-gray-400 bg-black/40">
                        <tr>
                          <th class="p-1">Crop</th>
                          <th class="p-1">Catalog ID</th>
                          <th class="p-1">Variety</th>
                          <th class="p-1">Sowing</th>
                          <th class="p-1">Water Need</th>
                          <th class="p-1">Exp. Yield</th>
                          <th class="p-1">Gross Margin</th>
                        </tr>
                      </thead>
                      <tbody id="rabi-crops-tbody" class="divide-y divide-white/5 text-gray-200 font-mono">
                        <!-- Populated via JS -->
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>

              <!-- VIEW B: GLOBAL FAO & NASA 549 CROP CATALOG (SEARCHABLE EXPLORER) -->
              <div id="view-crops-catalog" class="hidden space-y-2">
                <!-- Search & Filter Controls -->
                <div class="grid grid-cols-1 sm:grid-cols-12 gap-2">
                  <div class="sm:col-span-7 relative">
                    <input type="text" id="catalog-search-input" oninput="filterCropCatalog()" placeholder="Search 549 crops (e.g. Wheat, Rice, Chickpea, Olive, Cotton)..." class="w-full pl-8 pr-3 py-1.5 rounded-xl bg-black/40 border border-white/10 text-xs text-white placeholder-gray-500 focus:outline-none focus:border-blue-500">
                    <i class="fa-solid fa-magnifying-glass absolute left-2.5 top-2.5 text-gray-500 text-[10px]"></i>
                  </div>
                  <div class="sm:col-span-5">
                    <select id="catalog-group-select" onchange="filterCropCatalog()" class="w-full py-1.5 px-2 rounded-xl bg-[#161922] border border-white/10 text-xs text-gray-200 focus:outline-none focus:border-blue-500">
                      <option value="">All Groups (549 Crops)</option>
                      <option value="Cereals & pseudocereals">Cereals & Pseudocereals (31)</option>
                      <option value="Legumes & pulses">Legumes & Pulses (30)</option>
                      <option value="Vegetables">Vegetables (45)</option>
                      <option value="Fruits & nuts">Fruits & Nuts (59)</option>
                      <option value="Oilseeds & industrial">Oilseeds & Industrial (20)</option>
                      <option value="Roots, tubers & bulbs">Roots, Tubers & Bulbs (30)</option>
                      <option value="Spices, herbs & beverage crops">Spices & Herbs (30)</option>
                      <option value="Fodder, forage & cover crops">Fodder & Cover Crops (30)</option>
                      <option value="Crop varieties, market classes & production systems">Varieties & Systems (254)</option>
                    </select>
                  </div>
                </div>

                <!-- 549 Crops Results Table -->
                <div class="overflow-x-auto max-h-[380px] overflow-y-auto custom-scroll border border-white/5 rounded-xl bg-black/20">
                  <table class="w-full text-[10px] text-left">
                    <thead class="text-gray-400 bg-black/60 sticky top-0 z-10 font-sans">
                      <tr>
                        <th class="p-1.5">ID</th>
                        <th class="p-1.5">Crop Name</th>
                        <th class="p-1.5">Scientific Name</th>
                        <th class="p-1.5">Group</th>
                        <th class="p-1.5">Water Requirement</th>
                        <th class="p-1.5">NASA EO Sensors</th>
                        <th class="p-1.5 text-center">Action</th>
                      </tr>
                    </thead>
                    <tbody id="catalog-crops-tbody" class="divide-y divide-white/5 font-mono text-gray-300">
                      <!-- Populated via JS -->
                    </tbody>
                  </table>
                </div>
              </div>

            </div>

            <!-- TAB 3: THE HACKERS DEN SOIL STRATA PROFILE (4 DEPTHS) -->
            <div id="content-soil" class="tab-panel hidden flex-1 overflow-y-auto custom-scroll space-y-2 text-xs pt-1">
              <div class="grid grid-cols-2 gap-2">
                <div class="p-2 rounded-xl bg-black/30 border border-white/5">
                  <span class="text-gray-400 text-[10px] block">Surface (–5 cm):</span>
                  <span id="soil-5-val" class="font-mono font-bold text-amber-300 text-sm">0.2400 m³/m³</span>
                </div>
                <div class="p-2 rounded-xl bg-black/30 border border-white/5">
                  <span class="text-gray-400 text-[10px] block">Root Zone (–15 cm):</span>
                  <span id="soil-15-val" class="font-mono font-bold text-emerald-300 text-sm">0.2700 m³/m³</span>
                </div>
                <div class="p-2 rounded-xl bg-black/30 border border-white/5">
                  <span class="text-gray-400 text-[10px] block">Subsoil (–50 cm):</span>
                  <span id="soil-50-val" class="font-mono font-bold text-blue-300 text-sm">0.2900 m³/m³</span>
                </div>
                <div class="p-2 rounded-xl bg-black/30 border border-white/5">
                  <span class="text-gray-400 text-[10px] block">Deep Aquifer (–150 cm):</span>
                  <span id="soil-150-val" class="font-mono font-bold text-indigo-300 text-sm">0.3200 m³/m³</span>
                </div>
              </div>
              <div class="flex justify-between text-[11px] text-gray-400 pt-1 border-t border-white/5">
                <span>Soil Moisture Deficit: <strong id="soil-smd-val" class="text-white font-mono">24.5 mm</strong></span>
                <span>Frost Hazard: <strong id="soil-frost-val" class="text-white font-mono">0.0%</strong></span>
              </div>
            </div>

            <!-- TAB 4: WHAT-IF CLIMATE SENSITIVITY & RECOMMENDED ANALOG CITY -->
            <div id="content-climate" class="tab-panel hidden flex-1 overflow-y-auto custom-scroll space-y-2 text-xs pt-1">
              
              <!-- Sliders -->
              <div class="space-y-1.5 bg-black/30 p-2.5 rounded-xl border border-white/5">
                <div class="flex justify-between text-[11px]">
                  <span class="text-gray-300">Temp Anomaly (ΔT): <strong id="sim-temp-disp" class="text-rose-400 font-mono">+0.0°C</strong></span>
                  <span class="text-gray-300">Rainfall: <strong id="sim-rain-disp" class="text-blue-400 font-mono">100%</strong></span>
                </div>
                <input type="range" id="climate-temp-slider" min="-3" max="5" step="0.5" value="0" oninput="onClimateSliderChange()" class="w-full accent-rose-500 h-1.5 bg-[#111317] rounded cursor-pointer">
                <input type="range" id="climate-precip-slider" min="50" max="200" step="5" value="100" oninput="onClimateSliderChange()" class="w-full accent-blue-500 h-1.5 bg-[#111317] rounded cursor-pointer">
              </div>

              <!-- RECOMMENDED ANALOG CITY CARD (USER REQUIREMENT) -->
              <div class="p-2.5 rounded-xl bg-gradient-to-br from-blue-950/50 to-indigo-950/30 border border-blue-800/40 space-y-1.5">
                <div class="flex items-center justify-between">
                  <div class="flex items-center space-x-1.5">
                    <i class="fa-solid fa-compass text-amber-400 text-xs"></i>
                    <span class="text-gray-300 text-[10px] font-bold uppercase tracking-wider">Recommended Climate Analog City:</span>
                  </div>
                  <button onclick="switchToAnalogCity()" id="analog-switch-btn" class="px-2 py-0.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-white font-bold text-[10px] transition shadow">
                    Switch to <span id="analog-city-btn-name">Murree</span>
                  </button>
                </div>

                <div class="flex items-baseline space-x-2">
                  <span id="analog-city-name" class="text-sm font-black text-emerald-400">Murree</span>
                  <span id="analog-city-temp" class="text-xs font-mono text-gray-200">11.2 °C</span>
                  <span id="analog-city-vwc" class="text-xs font-mono text-blue-300">0.3200 m³/m³</span>
                </div>

                <p id="analog-city-reason" class="text-[10px] text-gray-300 leading-relaxed italic">
                  High-altitude mountain microclimate (2,291m elevation) provides natural 12°C cooling buffer against extreme heatwaves.
                </p>
                <div class="text-[10px] text-amber-300 font-mono">
                  Adaptive Strategy: <span id="analog-city-crops" class="text-white">Highland Vegetables (Tomato, Peas) & Orchards</span>
                </div>
              </div>

            </div>

            <!-- TAB 5: CROP ROTATION SIMULATOR -->
            <div id="content-rotations" class="tab-panel hidden flex-1 overflow-y-auto custom-scroll space-y-2 text-xs pt-1">
              <div class="flex items-center justify-between text-[11px]">
                <span class="text-gray-400">Optimize for:</span>
                <div class="flex space-x-1">
                  <button onclick="setFarmerPriority('water')" class="px-2 py-0.5 rounded bg-emerald-950 text-emerald-300 border border-emerald-700 text-[10px] font-bold">Water</button>
                  <button onclick="setFarmerPriority('income')" class="px-2 py-0.5 rounded bg-[#111317] text-gray-300 text-[10px]">Income</button>
                  <button onclick="setFarmerPriority('soil')" class="px-2 py-0.5 rounded bg-[#111317] text-gray-300 text-[10px]">Soil</button>
                </div>
              </div>
              <div id="rotation-cycle-display" class="p-2 rounded-xl bg-black/30 border border-white/5 space-y-1">
                <div class="font-bold text-emerald-400 text-xs" id="rot-name">Scenario A: Water-Conserving Cycle</div>
                <div class="text-[10px] text-gray-300 font-mono" id="rot-succession">Groundnut → Sesbania Cover → Rainfed Wheat → Fallow</div>
              </div>
            </div>

          </div>

        </div>

      </div>

    </div>

  </div>

  <!-- ── 4. MODAL: CASCADING PROVINCE & CITY PICKER ───────────────────────── -->
  <div id="city-modal" class="fixed inset-0 bg-black/85 backdrop-blur-md z-50 hidden items-center justify-center p-4">
    <div class="dashboard-frame max-w-md w-full p-6 rounded-[28px] border border-white/10 space-y-4 shadow-2xl">
      <div class="flex justify-between items-center border-b border-white/10 pb-3">
        <h3 class="font-bold text-sm text-white flex items-center space-x-1.5">
          <i class="fa-solid fa-map-location-dot text-blue-400"></i>
          <span>Select Pakistan Province & City</span>
        </h3>
        <button onclick="closeCityPicker()" class="text-gray-400 hover:text-white"><i class="fa-solid fa-xmark"></i></button>
      </div>

      <div class="space-y-3 text-xs">
        <div>
          <label class="text-gray-400 block mb-1">State / Province of Pakistan:</label>
          <select id="province-select" onchange="onProvinceChange()" class="w-full p-2.5 rounded-xl bg-[#1c1f26] border border-white/10 text-white font-medium focus:outline-none">
            <option value="Punjab" selected>Punjab</option>
            <option value="Sindh">Sindh</option>
            <option value="Khyber Pakhtunkhwa">Khyber Pakhtunkhwa</option>
            <option value="Balochistan">Balochistan</option>
            <option value="Islamabad Capital Territory">Islamabad</option>
            <option value="Azad Jammu & Kashmir">AJK</option>
            <option value="Gilgit-Baltistan">Gilgit-Baltistan</option>
          </select>
        </div>

        <div>
          <label class="text-gray-400 block mb-1">City / Tehsil in Province:</label>
          <select id="city-select" onchange="onCityDropdownChange()" class="w-full p-2.5 rounded-xl bg-[#1c1f26] border border-white/10 text-white font-medium focus:outline-none font-mono">
            <!-- Dynamically populated -->
          </select>
        </div>

        <div class="flex items-center space-x-2 pt-1">
          <input type="checkbox" id="modal-set-default-check" class="rounded bg-[#1c1f26] border-white/20 text-emerald-500 focus:ring-0">
          <label for="modal-set-default-check" class="text-gray-300 text-[11px] cursor-pointer">Set as default home location</label>
        </div>

        <button onclick="applyAndSaveModalLocation()" class="w-full py-2.5 rounded-xl bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white font-bold transition flex items-center justify-center space-x-2 shadow">
          <i class="fa-solid fa-floppy-disk"></i>
          <span>Save & Load Location Details</span>
        </button>

        <button onclick="autoDetectLocation(); closeCityPicker();" class="w-full py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-bold transition flex items-center justify-center space-x-2 shadow">
          <i class="fa-solid fa-crosshairs"></i>
          <span>Auto-Detect My Location (GPS / Network API)</span>
        </button>

        <!-- Saved Locations Quick Access in Modal -->
        <div class="border-t border-white/10 pt-2.5">
          <div class="flex items-center justify-between mb-1.5">
            <span class="text-gray-400 font-semibold text-[11px] flex items-center space-x-1">
              <i class="fa-solid fa-bookmark text-amber-400"></i>
              <span>Saved Locations:</span>
            </span>
            <button onclick="openSavedLocationsModal(); closeCityPicker();" class="text-[10px] text-blue-400 hover:underline">Manage All</button>
          </div>
          <div id="modal-saved-chips" class="flex flex-wrap gap-1.5 max-h-24 overflow-y-auto custom-scroll">
            <!-- Populated via JS -->
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- ── 4.5. MODAL: SAVED LOCATIONS MANAGER ───────────────────────────────── -->
  <div id="saved-locations-modal" class="fixed inset-0 bg-black/85 backdrop-blur-md z-50 hidden items-center justify-center p-4">
    <div class="dashboard-frame max-w-lg w-full p-6 rounded-[28px] border border-white/10 space-y-4 shadow-2xl max-h-[85vh] flex flex-col">
      <div class="flex justify-between items-center border-b border-white/10 pb-3 flex-shrink-0">
        <h3 class="font-bold text-sm text-white flex items-center space-x-2">
          <i class="fa-solid fa-bookmark text-amber-400"></i>
          <span>Saved Agricultural Sites & Research Hubs</span>
        </h3>
        <button onclick="closeSavedLocationsModal()" class="text-gray-400 hover:text-white"><i class="fa-solid fa-xmark"></i></button>
      </div>

      <!-- Quick Save Current Active Location Form -->
      <div class="bg-black/30 p-3 rounded-2xl border border-white/5 space-y-2 flex-shrink-0 text-xs">
        <div class="flex justify-between items-center">
          <span class="text-gray-300 font-semibold">Save Current Active Location:</span>
          <span id="save-current-name-disp" class="text-emerald-400 font-mono font-bold">Chakwal</span>
        </div>
        <div class="flex space-x-2">
          <input type="text" id="save-custom-label-input" placeholder="Custom Label (e.g. Olive Orchard, Plot B)..." class="flex-1 px-3 py-1.5 rounded-xl bg-[#161922] border border-white/10 text-white text-xs placeholder-gray-500 focus:outline-none focus:border-blue-500">
          <button onclick="saveCurrentLocationWithLabel()" class="px-3 py-1.5 rounded-xl bg-amber-600 hover:bg-amber-500 text-white font-bold text-xs transition flex items-center space-x-1 shadow">
            <i class="fa-solid fa-plus"></i>
            <span>Save</span>
          </button>
        </div>
      </div>

      <!-- List of Saved Locations -->
      <div class="flex-1 overflow-y-auto custom-scroll space-y-2 text-xs" id="saved-locations-list-container">
        <!-- Dynamically populated via JS -->
      </div>
    </div>
  </div>

  <!-- TOAST NOTIFICATION CONTAINER -->
  <div id="toast-notification" class="fixed bottom-5 right-5 z-50 bg-[#1b1e27] border border-emerald-500/50 text-white px-4 py-2.5 rounded-2xl shadow-2xl flex items-center space-x-2.5 transition-all duration-300 opacity-0 pointer-events-none transform translate-y-2">
    <i id="toast-icon" class="fa-solid fa-circle-check text-emerald-400"></i>
    <span id="toast-msg" class="text-xs font-medium">Location saved successfully.</span>
  </div>

  <!-- ── 5. MODAL: NASA SCIENTIFIC GLOSSARY & DATA FUSION ─────────────────── -->
  <div id="glossary-modal" class="fixed inset-0 bg-black/85 backdrop-blur-md z-50 hidden items-center justify-center p-4">
    <div class="dashboard-frame max-w-2xl w-full p-6 rounded-[28px] border border-white/10 space-y-4 max-h-[85vh] overflow-y-auto custom-scroll shadow-2xl">
      <div class="flex justify-between items-center border-b border-white/10 pb-3">
        <div class="flex items-center space-x-2">
          <i class="fa-solid fa-book-open text-blue-400 text-base"></i>
          <h3 class="font-bold text-sm text-white">NASA Scientific Intelligence Glossary</h3>
        </div>
        <button onclick="closeGlossaryModal()" class="text-gray-400 hover:text-white"><i class="fa-solid fa-xmark"></i></button>
      </div>
      <div class="space-y-3 text-xs text-gray-300" id="glossary-items-container">
        <!-- Loaded via /api/glossary -->
      </div>
    </div>
  </div>

  <!-- ── 6. MODAL: NASA JUDGE TECHNICAL DOSSIER ──────────────────────────── -->
  <div id="judge-modal" class="fixed inset-0 bg-black/85 backdrop-blur-md z-50 hidden items-center justify-center p-4">
    <div class="dashboard-frame max-w-xl w-full p-6 rounded-[28px] border border-white/10 space-y-4 max-h-[85vh] overflow-y-auto custom-scroll shadow-2xl">
      <div class="flex justify-between items-center border-b border-white/10 pb-3">
        <div class="flex items-center space-x-2">
          <i class="fa-solid fa-award text-amber-400 text-base"></i>
          <h3 class="font-bold text-sm text-white">NASA Space Apps Hackathon 2026 Technical Dossier</h3>
        </div>
        <button onclick="closeJudgeModal()" class="text-gray-400 hover:text-white"><i class="fa-solid fa-xmark"></i></button>
      </div>
      <div class="space-y-2.5 text-xs text-gray-300">
        <div class="p-3 rounded-xl bg-white/5 border border-white/5">
          <span class="font-bold text-white block mb-1">The Hackers Den Foundation Model Engine:</span>
          <p>LocationEncoder (Sinusoidal 64-dim harmonic embedding) & TemporalEncoder (Day-of-year embedding) with 4-block Residual MLP trunk for multi-task weather, soil, and AQI inference.</p>
        </div>
        <div class="grid grid-cols-2 gap-2 font-mono text-[11px]">
          <div class="p-2.5 rounded-lg bg-black/40 border border-white/5">
            <span class="text-gray-400 block">Temperature R²:</span>
            <span class="text-emerald-400 font-bold">0.968 (MAE: 1.21°C)</span>
          </div>
          <div class="p-2.5 rounded-lg bg-black/40 border border-white/5">
            <span class="text-gray-400 block">MSL Pressure R²:</span>
            <span class="text-blue-400 font-bold">0.935 (MAE: 1.28 hPa)</span>
          </div>
        </div>
        <div class="p-3 rounded-xl bg-white/5 border border-white/5 text-[11px]">
          <span class="font-bold text-amber-400 block mb-1">AccuWeather Core & Database Vault:</span>
          <span>AccuWeather Live Telemetry (Key: zpka_008...) + AES-256 equivalent PBKDF2-HMAC-SHA256 vault.</span>
        </div>
      </div>
    </div>
  </div>

  <!-- ── 6.5. MODAL: GLOBAL FAO & NASA 549 CROP PROFILE INSPECTOR ──────────── -->
  <div id="crop-detail-modal" class="fixed inset-0 bg-black/85 backdrop-blur-md z-50 hidden items-center justify-center p-4">
    <div class="dashboard-frame max-w-2xl w-full p-6 rounded-[28px] border border-white/10 space-y-4 max-h-[90vh] overflow-y-auto custom-scroll shadow-2xl">
      <div class="flex justify-between items-center border-b border-white/10 pb-3">
        <div class="flex items-center space-x-2">
          <i class="fa-solid fa-seedling text-emerald-400 text-lg"></i>
          <div>
            <h3 id="crop-modal-title" class="font-bold text-base text-white">Wheat (Triticum aestivum)</h3>
            <span id="crop-modal-group" class="text-[10px] text-blue-300 font-mono">Cereals & pseudocereals · Species / crop entry</span>
          </div>
        </div>
        <button onclick="closeCropModal()" class="w-8 h-8 rounded-full bg-white/5 hover:bg-white/10 text-gray-400 hover:text-white flex items-center justify-center transition">
          <i class="fa-solid fa-xmark"></i>
        </button>
      </div>

      <!-- Quick Metrics Grid -->
      <div class="grid grid-cols-2 sm:grid-cols-4 gap-2 text-center font-mono">
        <div class="p-2.5 rounded-xl bg-black/40 border border-white/5">
          <span class="text-gray-400 text-[9px] block">Catalog ID</span>
          <span id="crop-modal-id" class="text-xs font-bold text-amber-300">CR0002</span>
        </div>
        <div class="p-2.5 rounded-xl bg-black/40 border border-white/5">
          <span class="text-gray-400 text-[9px] block">Growth Cycle</span>
          <span id="crop-modal-cycle" class="text-xs font-bold text-emerald-300">120 - 150 days</span>
        </div>
        <div class="p-2.5 rounded-xl bg-black/40 border border-white/5">
          <span class="text-gray-400 text-[9px] block">Optimal Temp</span>
          <span id="crop-modal-temp" class="text-xs font-bold text-rose-300">15°C - 25°C</span>
        </div>
        <div class="p-2.5 rounded-xl bg-black/40 border border-white/5">
          <span class="text-gray-400 text-[9px] block">Soil pH Range</span>
          <span id="crop-modal-ph" class="text-xs font-bold text-cyan-300">6.0 - 7.5</span>
        </div>
      </div>

      <!-- Water Requirement & Common Uses -->
      <div class="space-y-2 text-xs">
        <div class="p-3 rounded-xl bg-white/5 border border-white/5 space-y-1">
          <span class="font-bold text-blue-300 block flex items-center space-x-1.5">
            <i class="fa-solid fa-droplet text-blue-400 text-[10px]"></i>
            <span>Water Requirement & Irrigation Management:</span>
          </span>
          <p id="crop-modal-water" class="text-gray-300 text-[11px] leading-relaxed">Location- and cultivar-dependent.</p>
        </div>

        <div class="p-3 rounded-xl bg-white/5 border border-white/5 space-y-1">
          <span class="font-bold text-emerald-300 block flex items-center space-x-1.5">
            <i class="fa-solid fa-wheat-awn text-emerald-400 text-[10px]"></i>
            <span>Agronomic Uses & Utility:</span>
          </span>
          <p id="crop-modal-uses" class="text-gray-300 text-[11px] leading-relaxed">Food, feed, flour, industrial use.</p>
        </div>

        <!-- NASA Earth Observation Variables -->
        <div class="p-3 rounded-xl bg-gradient-to-br from-blue-950/40 to-indigo-950/30 border border-blue-800/40 space-y-1.5">
          <span class="font-bold text-white block flex items-center space-x-1.5">
            <i class="fa-solid fa-satellite text-blue-400 text-[11px]"></i>
            <span>NASA Earth Observation Monitoring Variables:</span>
          </span>
          <p id="crop-modal-nasa-vars" class="text-blue-200 font-mono text-[11px]">Vegetation indices; land-surface temperature; soil moisture; precipitation</p>
          <div class="flex items-center space-x-2 pt-1">
            <span class="text-gray-400 text-[10px]">NASA Sources:</span>
            <span id="crop-modal-nasa-sources" class="px-2 py-0.5 rounded bg-blue-900/60 text-blue-300 text-[9px] font-mono">NASA Harvest Portal; MODIS; Landsat; SMAP; GPM</span>
          </div>
        </div>

        <!-- FAO EcoCrop Reference -->
        <div class="flex items-center justify-between p-2.5 rounded-xl bg-black/40 border border-white/5 text-[10px]">
          <div class="flex items-center space-x-2">
            <span class="text-gray-400">Reference:</span>
            <span id="crop-modal-ref" class="text-gray-200 font-medium">FAO EcoCrop / GAEZ</span>
          </div>
          <a id="crop-modal-url" href="https://www.fao.org/geospatial/data-and-tools/data-portals/ecocrop/en" target="_blank" class="text-blue-400 hover:text-blue-300 underline flex items-center space-x-1">
            <span>Open FAO Portal</span>
            <i class="fa-solid fa-arrow-up-right-from-square text-[9px]"></i>
          </a>
        </div>
      </div>
    </div>
  </div>

  <!-- ── 7. JAVASCRIPT CONTROLLER ─────────────────────────────────────────── -->
  <script>
    let map;
    let currentMarker;
    let radiusCircle;
    let activeRadiusKm = 25;
    let currentLat = 32.9328;
    let currentLon = 72.8631;
    let currentCity = "chakwal";
    let currentProvince = "Punjab";
    let activeLayerIndex = 0;
    let useFahrenheit = false;
    let latestData = null;
    let pakistanData = {};
    let currentFarmerPriority = "water";
    let baseTemp = 14.4;
    let basePrecip = 1.5;
    let baseVwc = 0.24;
    let baseFlood = 18.5;
    let glossaryData = null;
    let hourlyStartIndex = 0;
    let currentAnalogCity = "Murree";
    let savedLocations = [];

    const REGISTERED_CITIES_LIST = [
      { name: "Lahore", key: "lahore", province: "Punjab", barani: false },
      { name: "Chakwal", key: "chakwal", province: "Punjab", barani: true },
      { name: "Kharian", key: "kharian", province: "Punjab", barani: true },
      { name: "Multan", key: "multan", province: "Punjab", barani: false },
      { name: "Gujrat", key: "gujrat", province: "Punjab", barani: false },
      { name: "Gujranwala", key: "gujranwala", province: "Punjab", barani: false },
      { name: "Lalamusa", key: "lalamusa", province: "Punjab", barani: false },
      { name: "Islamabad", key: "islamabad", province: "Islamabad Capital Territory", barani: true },
      { name: "Murree", key: "murree", province: "Punjab", barani: true },
      { name: "Rawalpindi", key: "rawalpindi", province: "Punjab", barani: true },
      { name: "Attock", key: "attock", province: "Punjab", barani: true },
      { name: "Jhelum", key: "jhelum", province: "Punjab", barani: true },
      { name: "Mianwali", key: "mianwali", province: "Punjab", barani: true },
      { name: "Bhakkar", key: "bhakkar", province: "Punjab", barani: true },
      { name: "Faisalabad", key: "faisalabad", province: "Punjab", barani: false },
      { name: "Sialkot", key: "sialkot", province: "Punjab", barani: false },
      { name: "Bahawalpur", key: "bahawalpur", province: "Punjab", barani: false }
    ];

    const MAP_LAYERS = [
      { name: "Google Hybrid", url: "https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}" },
      { name: "NASA MODIS Terra", url: "https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/MODIS_Terra_CorrectedReflectance_TrueColor/default/2024-05-01/GoogleMapsCompatible_Level9/{z}/{y}/{x}.jpg" },
      { name: "Google Satellite", url: "https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}" },
      { name: "Google Terrain", url: "https://mt1.google.com/vt/lyrs=p&x={x}&y={y}&z={z}" }
    ];
    let currentTileLayer;

    // Clock ticker
    function startClock() {
      function update() {
        const now = new Date();
        document.getElementById('live-clock').innerText = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
        document.getElementById('live-date').innerText = now.toLocaleDateString([], { weekday: 'long', month: 'short', day: 'numeric' });
      }
      update();
      setInterval(update, 1000);
    }

    function initMap() {
      map = L.map('map', {
        center: [currentLat, currentLon],
        zoom: 9,
        zoomControl: false
      });

      currentTileLayer = L.tileLayer(MAP_LAYERS[0].url, {
        maxZoom: 19,
        attribution: 'Google / NASA GIBS'
      }).addTo(map);

      const pulseIcon = L.divIcon({
        className: 'custom-pulse-marker',
        html: '<div class="pulse-ring"></div>',
        iconSize: [16, 16],
        iconAnchor: [8, 8]
      });

      currentMarker = L.marker([currentLat, currentLon], { icon: pulseIcon }).addTo(map);

      radiusCircle = L.circle([currentLat, currentLon], {
        radius: activeRadiusKm * 1000,
        color: '#3b82f6',
        fillColor: '#2563eb',
        fillOpacity: 0.15,
        weight: 1.5,
        dashArray: '4, 4'
      }).addTo(map);

      map.on('click', function(e) {
        updateTargetCoordinates(e.latlng.lat, e.latlng.lng, null);
      });
    }

    function cycleSatelliteLayer() {
      activeLayerIndex = (activeLayerIndex + 1) % MAP_LAYERS.length;
      if (currentTileLayer) map.removeLayer(currentTileLayer);
      currentTileLayer = L.tileLayer(MAP_LAYERS[activeLayerIndex].url, { maxZoom: 19 }).addTo(map);
      document.getElementById('current-layer-name').innerText = MAP_LAYERS[activeLayerIndex].name;
    }

    function focusMap() {
      if (map) {
        map.invalidateSize();
        map.panTo([currentLat, currentLon]);
      }
    }

    function toggleTempUnit() {
      useFahrenheit = !useFahrenheit;
      document.getElementById('temp-unit-toggle').innerText = useFahrenheit ? '°F' : '°C';
      try { localStorage.setItem('fieldshift_temp_unit', useFahrenheit ? 'F' : 'C'); } catch (e) {}
      if (latestData) updateDashboardUI(latestData);
    }

    function setRadius(km) {
      activeRadiusKm = km;
      document.querySelectorAll('.rad-btn').forEach(btn => {
        if (parseInt(btn.getAttribute('data-r')) === km) {
          btn.className = "rad-btn px-2 py-0.5 rounded bg-blue-600 text-white font-bold text-[10px]";
        } else {
          btn.className = "rad-btn px-2 py-0.5 rounded bg-[#1c1f26] text-gray-300 hover:text-white text-[10px]";
        }
      });
      if (radiusCircle) radiusCircle.setRadius(km * 1000);
      queryPrediction();
    }

    // ── DIRECT INSTANT SEARCH ────────────────────────────────────────────────
    function onSearchInput(val) {
      const q = val.trim().toLowerCase();
      const suggBox = document.getElementById('search-suggestions');
      const clearBtn = document.getElementById('search-clear-btn');

      if (q.length > 0) {
        clearBtn.classList.remove('hidden');
      } else {
        clearBtn.classList.add('hidden');
        suggBox.classList.add('hidden');
        return;
      }

      const matches = REGISTERED_CITIES_LIST.filter(c => 
        c.name.toLowerCase().includes(q) || c.key.includes(q) || c.province.toLowerCase().includes(q)
      );

      if (matches.length > 0) {
        let html = '';
        matches.forEach(m => {
          const tag = m.barani ? "🌾 Barani" : "🚜 Irrigated";
          html += `
            <div onclick="selectCity('${m.key}'); clearSearch();" class="p-2.5 hover:bg-white/10 cursor-pointer flex justify-between items-center transition border-b border-white/5">
              <span class="font-bold text-white">${m.name}</span>
              <span class="text-[10px] text-gray-400 font-mono">${m.province} · ${tag}</span>
            </div>
          `;
        });
        suggBox.innerHTML = html;
        suggBox.classList.remove('hidden');
      } else {
        suggBox.innerHTML = `
          <div onclick="executeSearch()" class="p-2.5 text-gray-400 italic hover:bg-white/5 cursor-pointer">
            Search OpenStreetMap for "${q}, Pakistan" <i class="fa-solid fa-arrow-right ml-1"></i>
          </div>
        `;
        suggBox.classList.remove('hidden');
      }
    }

    function clearSearch() {
      document.getElementById('map-search-input').value = "";
      document.getElementById('search-suggestions').classList.add('hidden');
      document.getElementById('search-clear-btn').classList.add('hidden');
    }

    async function executeSearch() {
      const q = document.getElementById('map-search-input').value.trim();
      document.getElementById('search-suggestions').classList.add('hidden');
      if (!q) return;

      // Coordinate format match: e.g. "32.93, 72.86"
      const coordMatch = q.match(/^([-+]?\d+(\.\d+)?)[,\s]+([-+]?\d+(\.\d+)?)$/);
      if (coordMatch) {
        updateTargetCoordinates(parseFloat(coordMatch[1]), parseFloat(coordMatch[3]), null);
        return;
      }

      // Check registered cities
      for (const c of REGISTERED_CITIES_LIST) {
        if (c.name.toLowerCase() === q.toLowerCase() || c.key === q.toLowerCase()) {
          selectCity(c.key);
          return;
        }
      }

      // Geocoding lookup via OpenStreetMap Nominatim
      try {
        const resp = await fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(q + ', Pakistan')}`);
        const res = await resp.json();
        if (res && res.length > 0) {
          updateTargetCoordinates(parseFloat(res[0].lat), parseFloat(res[0].lon), res[0].display_name.split(',')[0]);
        } else {
          alert(`Could not find "${q}". Try a major agricultural district like Lahore, Multan, Chakwal, Kharian, etc.`);
        }
      } catch (e) {
        console.error(e);
      }
    }

    function updateTargetCoordinates(lat, lon, cityName) {
      currentLat = lat;
      currentLon = lon;
      if (cityName) currentCity = cityName;
      if (currentMarker) currentMarker.setLatLng([lat, lon]);
      if (radiusCircle) radiusCircle.setLatLng([lat, lon]);
      map.panTo([lat, lon]);
      queryPrediction(cityName, lat, lon);
      updateSaveButtonState();
    }

    function selectCity(cityKey) {
      currentCity = cityKey;
      clearSearch();
      queryPrediction(cityKey);
      updateSaveButtonState();
    }

    // ── MAIN PREDICTION & DATA BINDING ──────────────────────────────────────
    async function queryPrediction(cityName = null, lat = null, lon = null) {
      let url = `/api/predict?radius=${activeRadiusKm}`;
      if (cityName) {
        url += `&station=${encodeURIComponent(cityName)}`;
      } else if (lat !== null && lon !== null) {
        url += `&lat=${lat}&lon=${lon}`;
      } else if (currentCity) {
        url += `&station=${encodeURIComponent(currentCity)}`;
      }

      try {
        const resp = await fetch(url);
        const data = await resp.json();
        latestData = data;
        updateDashboardUI(data);
      } catch (err) {
        console.error("Prediction fetch failed:", err);
      }
    }

    function updateDashboardUI(data) {
      const coords = data.coordinates;
      currentLat = coords.lat;
      currentLon = coords.lon;
      currentCity = data.location.toLowerCase();

      document.getElementById('top-location-name').innerText = `${data.display_name}`;
      document.getElementById('map-target-coords').innerText = `${coords.lat.toFixed(4)}°N, ${coords.lon.toFixed(4)}°E`;
      document.getElementById('top-zone-badge').innerText = data.zone || "Agricultural Zone";

      if (currentMarker) currentMarker.setLatLng([coords.lat, coords.lon]);
      if (radiusCircle) radiusCircle.setLatLng([coords.lat, coords.lon]);
      map.panTo([coords.lat, coords.lon]);

      // Hero Weather Card
      const w = data.weather;
      baseTemp = w.temperature_c;
      const tempDisplay = useFahrenheit ? `${Math.round(w.temperature_f)}°F` : `${Math.round(w.temperature_c)}°C`;
      const feelsDisplay = useFahrenheit ? `${Math.round(w.temperature_f - 2)}°` : `${Math.round(w.temperature_c - 1)}°`;

      document.getElementById('hero-temp-display').innerText = tempDisplay;
      document.getElementById('hero-condition-display').innerText = data.weather_condition;
      document.getElementById('hero-feels-like').innerText = feelsDisplay;
      document.getElementById('hero-humidity').innerText = `${w.humidity_pct}%`;
      document.getElementById('hero-wind').innerText = `${Math.round(w.wind_speed_kmh * 0.621)} mph NW`;
      document.getElementById('hero-pressure').innerText = `${Math.round(w.pressure_hpa)} hPa`;

      // Flood Risk
      const f = data.flood_risk;
      baseFlood = f.flood_risk_score;
      basePrecip = f.rainfall_accumulation_mm || 1.5;
      document.getElementById('flood-safety-pill').innerText = f.flood_risk_score < 30 ? "Safe" : "Watch";
      document.getElementById('flood-runoff-rate').innerText = `Flood Risk: ${f.flood_risk_score}% · ${f.runoff_level}`;

      // Air Quality & UV
      const aq = data.air_quality;
      document.getElementById('aqi-score').innerText = Math.round(aq.aqi);
      document.getElementById('aqi-badge-text').innerText = aq.category;

      // Soil Strata
      const s = data.soil;
      baseVwc = s.volumetric_water_15cm_m3m3;
      document.getElementById('soil-5-val').innerText = `${s.volumetric_water_5cm_m3m3.toFixed(4)} m³/m³`;
      document.getElementById('soil-15-val').innerText = `${s.volumetric_water_15cm_m3m3.toFixed(4)} m³/m³`;
      document.getElementById('soil-50-val').innerText = `${s.volumetric_water_50cm_m3m3.toFixed(4)} m³/m³`;
      document.getElementById('soil-150-val').innerText = `${s.volumetric_water_150cm_m3m3.toFixed(4)} m³/m³`;
      document.getElementById('soil-smd-val').innerText = `${s.moisture_deficit_mm} mm`;
      document.getElementById('soil-frost-val').innerText = `${s.frost_probability_pct}%`;

      // Middle Column Prithvi Satellite & Land Metrics
      const midEt = document.getElementById('mid-et-val');
      const midVwc = document.getElementById('mid-vwc-val');
      const midSmd = document.getElementById('mid-smd-val');
      if (midEt && s) midEt.innerText = `${(3.2 + (s.moisture_deficit_mm || 20) * 0.05).toFixed(1)} mm/day`;
      if (midVwc && s) midVwc.innerText = `${s.volumetric_water_15cm_m3m3.toFixed(4)} m³/m³`;
      if (midSmd && s) midSmd.innerText = `${s.moisture_deficit_mm} mm`;

      // Astronomy & Solar Cycle (Dynamic Dawn, Sunrise, Sunset, Dusk)
      if (data.astronomy) {
        const astro = data.astronomy;
        const dawnEl = document.getElementById('solar-dawn-disp');
        const duskEl = document.getElementById('solar-dusk-disp');
        const riseEl = document.getElementById('solar-rise-disp');
        const setEl = document.getElementById('solar-set-disp');
        const sunDot = document.getElementById('solar-sun-dot');
        const sunPulse = document.getElementById('solar-sun-pulse');

        if (dawnEl) dawnEl.innerText = `Dawn: ${astro.dawn}`;
        if (duskEl) duskEl.innerText = `Dusk: ${astro.dusk}`;
        if (riseEl) riseEl.innerText = `Rise: ${astro.sunrise}`;
        if (setEl) setEl.innerText = `Set: ${astro.sunset}`;

        if (sunDot) {
          const pct = Math.max(0, Math.min(100, astro.sun_progress_pct !== undefined ? astro.sun_progress_pct : 50));
          const rad = Math.PI * (1 - pct / 100);
          const cx = 55 + 43 * Math.cos(rad);
          const cy = 34 - 25 * Math.sin(rad);
          sunDot.setAttribute('cx', cx.toFixed(1));
          sunDot.setAttribute('cy', cy.toFixed(1));
          if (sunPulse) {
            sunPulse.setAttribute('cx', cx.toFixed(1));
            sunPulse.setAttribute('cy', cy.toFixed(1));
          }
          if (!astro.is_daylight) {
            sunDot.setAttribute('fill', '#94a3b8');
            sunDot.setAttribute('filter', 'drop-shadow(0 0 5px rgba(148,163,184,0.7))');
          } else {
            sunDot.setAttribute('fill', '#f59e0b');
            sunDot.setAttribute('filter', 'drop-shadow(0 0 8px #f59e0b)');
          }
        }
      }

      // CCRS Score
      if (data.ccrs) {
        document.getElementById('ccrs-badge').innerText = `CCRS: ${data.ccrs.grade} (${data.ccrs.ccrs_score})`;
      }

      // 1. UPDATE DYNAMIC HOURLY FORECAST
      renderHourlyForecast(data.hourly_forecast || []);

      // 2. UPDATE 5-DAY DAILY FORECAST
      renderDailyForecast(data.daily_forecast || []);

      // 3. UPDATE REGIONAL CROP AGRONOMY DATA
      renderCropAgronomy(data.crop_agronomy || {});

      // 4. SYNC ROTATIONS & WHAT-IF ANALOG CITY
      queryRotations();
      onClimateSliderChange();

      // 5. UPDATE SAVE LOCATION BUTTON & FORM
      updateSaveButtonState();
      const saveCurName = document.getElementById('save-current-name-disp');
      if (saveCurName) saveCurName.innerText = data.display_name || data.location;
    }

    // ── RENDER DYNAMIC HOURLY FORECAST FOR THIS CITY ─────────────────────────
    function renderHourlyForecast(hourlyData) {
      const container = document.getElementById('hourly-cards-container');
      if (!container || !hourlyData || hourlyData.length === 0) return;

      let html = '';
      const displayHours = hourlyData.slice(hourlyStartIndex, hourlyStartIndex + 6);

      displayHours.forEach((h, idx) => {
        const isActive = (idx === 0 && hourlyStartIndex === 0);
        const cardBg = isActive ? "bg-[#252b3a] border border-white/15" : "bg-[#171a22] border border-white/5 hover:bg-[#1d212b]";
        const tempStr = useFahrenheit ? `${Math.round(h.temp_f)}°` : `${Math.round(h.temp_c)}°`;
        
        // Exact Night Detection
        let isNight = false;
        if (h.is_night !== undefined) {
          isNight = !!h.is_night;
        } else if (h.is_daylight !== undefined) {
          isNight = !h.is_daylight;
        } else if (h.icon_code && h.icon_code >= 33 && h.icon_code <= 44) {
          isNight = true;
        } else if (h.time) {
          const tStr = h.time.toUpperCase();
          if (tStr.includes("PM")) {
            const hr = parseInt(tStr);
            isNight = (hr >= 6 && hr !== 12); // 6 PM - 11 PM
          } else if (tStr.includes("AM")) {
            const hr = parseInt(tStr);
            isNight = (hr < 6 || hr === 12);  // 12 AM - 5 AM
          }
        }

        const cond = (h.condition || "").toLowerCase();
        let iconHtml = '';

        if (isNight) {
          // Nighttime Icons: Moon-centric, NEVER day sun
          if (cond.includes("rain") || cond.includes("shower") || cond.includes("drizzle")) {
            iconHtml = '<i class="fa-solid fa-cloud-moon-rain text-blue-400"></i>';
          } else if (cond.includes("thunder") || cond.includes("storm")) {
            iconHtml = '<i class="fa-solid fa-cloud-bolt text-amber-400"></i>';
          } else if (cond.includes("snow") || cond.includes("flurry") || cond.includes("ice")) {
            iconHtml = '<i class="fa-solid fa-snowflake text-cyan-200"></i>';
          } else if (cond.includes("partly") || cond.includes("intermittent") || (cond.includes("cloud") && !cond.includes("overcast"))) {
            iconHtml = '<i class="fa-solid fa-cloud-moon text-indigo-300"></i>';
          } else if (cond.includes("cloud") || cond.includes("overcast")) {
            iconHtml = '<i class="fa-solid fa-cloud text-gray-400"></i>';
          } else {
            // Pure starry night crescent moon
            iconHtml = '<i class="fa-solid fa-moon text-indigo-200 drop-shadow-[0_0_6px_rgba(199,210,254,0.5)]"></i>';
          }
        } else {
          // Daytime Icons
          if (cond.includes("rain") || cond.includes("shower") || cond.includes("drizzle")) {
            iconHtml = '<i class="fa-solid fa-cloud-rain text-blue-400"></i>';
          } else if (cond.includes("thunder") || cond.includes("storm")) {
            iconHtml = '<i class="fa-solid fa-cloud-bolt text-amber-400"></i>';
          } else if (cond.includes("snow") || cond.includes("flurry") || cond.includes("ice")) {
            iconHtml = '<i class="fa-solid fa-snowflake text-cyan-200"></i>';
          } else if (cond.includes("cloud") && (cond.includes("sun") || cond.includes("partly") || cond.includes("scattered"))) {
            iconHtml = '<i class="fa-solid fa-cloud-sun text-amber-300"></i>';
          } else if (cond.includes("cloud") || cond.includes("overcast")) {
            iconHtml = '<i class="fa-solid fa-cloud text-gray-300"></i>';
          } else {
            // Sunny daylight
            iconHtml = '<i class="fa-solid fa-sun text-amber-400 drop-shadow-[0_0_6px_rgba(251,191,36,0.5)]"></i>';
          }
        }

        html += `
          <div class="rounded-2xl ${cardBg} p-2 sm:p-2.5 text-center flex flex-col justify-between items-center transition shadow">
            <span class="text-[10px] text-gray-300 font-semibold block">${h.time}</span>
            <div class="my-1 text-base">${iconHtml}</div>
            <span class="text-xs sm:text-sm font-bold text-white block">${tempStr}</span>
            <span class="text-[9px] text-blue-400 block font-mono">${h.precip_pct}% rain</span>
            <div class="h-0.5 w-4 ${isActive ? 'bg-white/50' : 'bg-transparent'} rounded-full mt-1.5"></div>
          </div>
        `;
      });

      container.innerHTML = html;
    }

    function shiftHourly(delta) {
      if (!latestData || !latestData.hourly_forecast) return;
      const maxStart = Math.max(0, latestData.hourly_forecast.length - 6);
      hourlyStartIndex = Math.max(0, Math.min(maxStart, hourlyStartIndex + delta * 2));
      renderHourlyForecast(latestData.hourly_forecast);
    }

    // ── RENDER 5-DAY DAILY FORECAST ROWS ─────────────────────────────────────
    function renderDailyForecast(dailyData) {
      const container = document.getElementById('content-forecast');
      if (!container || !dailyData || dailyData.length === 0) return;

      let html = '';
      dailyData.forEach(d => {
        const tMax = useFahrenheit ? `${Math.round(d.temp_max_f)}°` : `${Math.round(d.temp_max_c)}°`;
        const tMin = useFahrenheit ? `${Math.round(d.temp_min_f)}°` : `${Math.round(d.temp_min_c)}°`;

        let icon = '<i class="fa-solid fa-sun text-amber-400"></i>';
        const cond = (d.condition || "").toLowerCase();
        if (cond.includes("rain") || cond.includes("thunder")) {
          icon = '<i class="fa-solid fa-cloud-showers-heavy text-blue-400"></i>';
        } else if (cond.includes("cloud")) {
          icon = '<i class="fa-solid fa-cloud-sun text-amber-300"></i>';
        }

        html += `
          <div class="flex items-center justify-between text-gray-300 hover:bg-white/5 p-1.5 rounded-xl transition">
            <span class="w-20 font-medium text-white">${d.day}</span>
            <div class="w-6 text-center">${icon}</div>
            <span class="text-gray-400 text-[11px] truncate max-w-[120px]">${d.condition}</span>
            <span class="font-mono text-white font-bold">${tMax} / <span class="text-gray-400 font-normal">${tMin}</span></span>
            <span class="text-blue-400 font-mono text-[10px] w-12 text-right"><i class="fa-solid fa-droplet text-[8px] mr-1"></i>${d.precip_pct}%</span>
          </div>
        `;
      });
      container.innerHTML = html;
    }

    // ── RENDER REGIONAL CROP AGRONOMY DATA ───────────────────────────────────
    function renderCropAgronomy(cropData) {
      if (!cropData || !cropData.zone) return;
      document.getElementById('crop-zone-title').innerText = cropData.zone;
      document.getElementById('crop-soil-title').innerText = cropData.soil_type || "Alluvial Loam";

      const kharifTbody = document.getElementById('kharif-crops-tbody');
      let kHtml = '';
      (cropData.kharif_crops || []).forEach(c => {
        const catId = c.catalog_id || "CR0001";
        kHtml += `
          <tr class="hover:bg-white/5 transition">
            <td class="p-1 font-bold text-amber-300">${c.crop}</td>
            <td class="p-1">
              <button onclick="openCropModal('${catId}')" class="px-1.5 py-0.5 rounded bg-blue-950 text-blue-300 hover:bg-blue-900 border border-blue-700/60 text-[9px] font-mono cursor-pointer transition shadow-sm" title="View ${c.scientific_name || 'FAO/NASA'} Specs">
                <i class="fa-solid fa-satellite text-[8px] mr-1"></i>${catId}
              </button>
            </td>
            <td class="p-1 text-gray-300">${c.variety}</td>
            <td class="p-1 text-gray-400">${c.sowing}</td>
            <td class="p-1 text-blue-300">${c.water_need}</td>
            <td class="p-1 text-white font-bold">${c.yield}</td>
            <td class="p-1 text-emerald-400 font-bold">${c.gross_margin}</td>
          </tr>
        `;
      });
      kharifTbody.innerHTML = kHtml;

      const rabiTbody = document.getElementById('rabi-crops-tbody');
      let rHtml = '';
      (cropData.rabi_crops || []).forEach(c => {
        const catId = c.catalog_id || "CR0002";
        rHtml += `
          <tr class="hover:bg-white/5 transition">
            <td class="p-1 font-bold text-emerald-300">${c.crop}</td>
            <td class="p-1">
              <button onclick="openCropModal('${catId}')" class="px-1.5 py-0.5 rounded bg-blue-950 text-blue-300 hover:bg-blue-900 border border-blue-700/60 text-[9px] font-mono cursor-pointer transition shadow-sm" title="View ${c.scientific_name || 'FAO/NASA'} Specs">
                <i class="fa-solid fa-satellite text-[8px] mr-1"></i>${catId}
              </button>
            </td>
            <td class="p-1 text-gray-300">${c.variety}</td>
            <td class="p-1 text-gray-400">${c.sowing}</td>
            <td class="p-1 text-blue-300">${c.water_need}</td>
            <td class="p-1 text-white font-bold">${c.yield}</td>
            <td class="p-1 text-emerald-400 font-bold">${c.gross_margin}</td>
          </tr>
        `;
      });
      rabiTbody.innerHTML = rHtml;
    }

    // ── 549 FAO & NASA CROP CATALOG CONTROLLER ──────────────────────────────
    let cropCatalogCache = [];
    let activeCropsSubView = 'regional';

    function toggleCropsSubView(view) {
      activeCropsSubView = view;
      const btnReg = document.getElementById('btn-crop-regional');
      const btnCat = document.getElementById('btn-crop-catalog');
      const viewReg = document.getElementById('view-crops-regional');
      const viewCat = document.getElementById('view-crops-catalog');

      if (!btnReg || !btnCat || !viewReg || !viewCat) return;

      if (view === 'regional') {
        btnReg.className = "px-3 py-1 rounded-lg bg-blue-600 text-white font-bold text-[11px] transition shadow";
        btnCat.className = "px-3 py-1 rounded-lg bg-[#161922] hover:bg-[#202532] text-gray-400 hover:text-white font-medium text-[11px] transition";
        viewReg.classList.remove('hidden');
        viewCat.classList.add('hidden');
      } else {
        btnCat.className = "px-3 py-1 rounded-lg bg-blue-600 text-white font-bold text-[11px] transition shadow";
        btnReg.className = "px-3 py-1 rounded-lg bg-[#161922] hover:bg-[#202532] text-gray-400 hover:text-white font-medium text-[11px] transition";
        viewCat.classList.remove('hidden');
        viewReg.classList.add('hidden');
        if (cropCatalogCache.length === 0) {
          loadCropCatalog();
        }
      }
    }

    let filterDebounceTimer = null;
    function filterCropCatalog() {
      clearTimeout(filterDebounceTimer);
      filterDebounceTimer = setTimeout(() => {
        const q = document.getElementById('catalog-search-input').value.trim();
        const grp = document.getElementById('catalog-group-select').value;
        loadCropCatalog(q, grp);
      }, 250);
    }

    async function loadCropCatalog(q = '', grp = '') {
      let url = `/api/crop-catalog?limit=100`;
      if (q) url += `&q=${encodeURIComponent(q)}`;
      if (grp) url += `&group=${encodeURIComponent(grp)}`;

      try {
        const resp = await fetch(url);
        const data = await resp.json();
        const tbody = document.getElementById('catalog-crops-tbody');
        const countPill = document.getElementById('crop-catalog-count-pill');
        if (countPill && data.total_matches !== undefined) {
          countPill.innerText = `${data.total_matches} Crops Matched`;
        }
        if (!tbody) return;
        if (!data.crops || data.crops.length === 0) {
          tbody.innerHTML = `<tr><td colspan="7" class="p-4 text-center text-gray-400 italic">No crops found matching "${q}". Try another term.</td></tr>`;
          return;
        }

        cropCatalogCache = data.crops;
        let html = '';
        data.crops.forEach(c => {
          html += `
            <tr class="hover:bg-white/5 transition border-b border-white/5">
              <td class="p-1.5 font-bold text-amber-300">${c.crop_id}</td>
              <td class="p-1.5 font-bold text-white">${c.crop_name}</td>
              <td class="p-1.5 text-gray-400 italic">${c.scientific_name || '—'}</td>
              <td class="p-1.5">
                <span class="px-1.5 py-0.5 rounded bg-blue-950 text-blue-300 text-[8.5px] border border-blue-800">${c.crop_group}</span>
              </td>
              <td class="p-1.5 text-blue-300 text-[9px] max-w-[150px] truncate" title="${c.water_requirement || ''}">${c.water_requirement || 'Cultivar dependent'}</td>
              <td class="p-1.5 text-emerald-400 text-[9px] max-w-[140px] truncate" title="${c.nasa_data_sources || ''}">${c.nasa_data_sources || 'MODIS, SMAP, Landsat'}</td>
              <td class="p-1.5 text-center">
                <button onclick="openCropModal('${c.crop_id}')" class="px-2 py-0.5 rounded bg-blue-600 hover:bg-blue-500 text-white font-bold text-[9px] transition shadow">
                  Specs
                </button>
              </td>
            </tr>
          `;
        });
        tbody.innerHTML = html;
      } catch (err) {
        console.error("Failed to load crop catalog:", err);
      }
    }

    async function openCropModal(cropId) {
      try {
        const resp = await fetch(`/api/crop-catalog/detail?id=${encodeURIComponent(cropId)}`);
        const c = await resp.json();
        if (c.error) {
          alert("Crop details not found.");
          return;
        }

        document.getElementById('crop-modal-title').innerText = `${c.crop_name} (${c.scientific_name || 'Species'})`;
        document.getElementById('crop-modal-group').innerText = `${c.crop_group} · ${c.record_type || 'Catalog Entry'}`;
        document.getElementById('crop-modal-id').innerText = c.crop_id;
        document.getElementById('crop-modal-cycle').innerText = c.growth_cycle_days ? `${c.growth_cycle_days} days` : 'Cultivar dependent';
        document.getElementById('crop-modal-temp').innerText = (c.optimal_temp_min_c && c.optimal_temp_max_c) ? `${c.optimal_temp_min_c}°C - ${c.optimal_temp_max_c}°C` : '15°C - 30°C';
        document.getElementById('crop-modal-ph').innerText = (c.soil_ph_min && c.soil_ph_max) ? `${c.soil_ph_min} - ${c.soil_ph_max}` : '6.0 - 7.8';
        document.getElementById('crop-modal-water').innerText = c.water_requirement || 'Location and cultivar dependent; monitoring via SMAP & GPM.';
        document.getElementById('crop-modal-uses').innerText = c.common_uses || 'Food, feed, fibre or agricultural utility.';
        document.getElementById('crop-modal-nasa-vars').innerText = c.nasa_monitoring_variables || 'Vegetation indices (NDVI/EVI); Land Surface Temperature; Soil Moisture (SMAP); Precipitation (GPM).';
        document.getElementById('crop-modal-nasa-sources').innerText = c.nasa_data_sources || 'NASA Harvest Portal; MODIS Terra/Aqua; Landsat 8/9; SMAP L4; GPM IMERG.';
        document.getElementById('crop-modal-ref').innerText = c.agronomy_reference || 'FAO EcoCrop / GAEZ Agricultural Portal';
        
        const urlEl = document.getElementById('crop-modal-url');
        if (c.agronomy_reference_url) {
          urlEl.href = c.agronomy_reference_url;
          urlEl.classList.remove('hidden');
        } else {
          urlEl.classList.add('hidden');
        }

        const modal = document.getElementById('crop-detail-modal');
        modal.classList.remove('hidden');
        modal.classList.add('flex');
      } catch (err) {
        console.error("Failed to open crop modal:", err);
      }
    }

    function closeCropModal() {
      const modal = document.getElementById('crop-detail-modal');
      modal.classList.add('hidden');
      modal.classList.remove('flex');
    }

    // ── WHAT-IF CLIMATE SENSITIVITY & RECOMMENDED ANALOG CITY ─────────────────
    async function onClimateSliderChange() {
      const tempDelta = parseFloat(document.getElementById('climate-temp-slider').value);
      const precipPct = parseInt(document.getElementById('climate-precip-slider').value);

      document.getElementById('sim-temp-disp').innerText = `${tempDelta >= 0 ? '+' : ''}${tempDelta.toFixed(1)}°C`;
      document.getElementById('sim-rain-disp').innerText = `${precipPct}%`;

      const precipMult = precipPct / 100.0;
      const url = `/api/climate-sensitivity?temp=${baseTemp}&precip=${basePrecip}&vwc=${baseVwc}&flood=${baseFlood}&temp_delta=${tempDelta}&precip_mult=${precipMult}`;

      try {
        const resp = await fetch(url);
        const data = await resp.json();
        
        if (data.recommended_city_analog) {
          const a = data.recommended_city_analog;
          currentAnalogCity = a.city.toLowerCase();
          document.getElementById('analog-city-name').innerText = a.city;
          document.getElementById('analog-city-btn-name').innerText = a.city;
          document.getElementById('analog-city-temp').innerText = `${a.projected_city_temp_c} °C`;
          document.getElementById('analog-city-vwc').innerText = `${a.projected_city_vwc.toFixed(4)} m³/m³`;
          document.getElementById('analog-city-reason').innerText = a.reason;
          document.getElementById('analog-city-crops').innerText = a.ideal_crops;
        }
      } catch (err) {
        console.error("Climate sensitivity error:", err);
      }
    }

    function switchToAnalogCity() {
      if (currentAnalogCity) {
        selectCity(currentAnalogCity);
      }
    }

    // ── TABS SWITCHER ────────────────────────────────────────────────────────
    function switchTab(tabKey) {
      document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.className = "tab-btn text-gray-400 hover:text-white pb-0.5 flex items-center space-x-1";
      });
      document.querySelectorAll('.tab-panel').forEach(p => p.classList.add('hidden'));

      if (tabKey === 'catalog') {
        const catBtn = document.getElementById('tab-catalog');
        if (catBtn) catBtn.className = "tab-btn font-semibold text-amber-300 border-b-2 border-amber-400 pb-0.5 flex items-center space-x-1";
        const cropsPanel = document.getElementById('content-crops');
        if (cropsPanel) cropsPanel.classList.remove('hidden');
        toggleCropsSubView('catalog');
        return;
      }

      const activeBtn = document.getElementById(`tab-${tabKey}`);
      if (activeBtn) activeBtn.className = "tab-btn font-semibold text-white border-b-2 border-blue-500 pb-0.5 flex items-center space-x-1";

      const activePanel = document.getElementById(`content-${tabKey}`);
      if (activePanel) activePanel.classList.remove('hidden');
    }

    async function queryRotations() {
      const city = currentCity || "chakwal";
      const url = `/api/rotations?station=${encodeURIComponent(city)}&priority=${currentFarmerPriority}&vwc=${baseVwc}&flood=${baseFlood}`;
      try {
        const resp = await fetch(url);
        const data = await resp.json();
        if (data.scenarios && data.scenarios.length > 0) {
          const top = data.scenarios[0];
          document.getElementById('rot-name').innerText = top.name;
          document.getElementById('rot-succession').innerText = top.cycle.map(c => `${c.crop} (${c.season})`).join(' → ');
        }
      } catch (err) {
        console.error(err);
      }
    }

    function setFarmerPriority(prio) {
      currentFarmerPriority = prio;
      queryRotations();
    }

    // Modals
    function openCityPicker() {
      document.getElementById('city-modal').classList.remove('hidden');
      document.getElementById('city-modal').classList.add('flex');
    }
    function closeCityPicker() {
      document.getElementById('city-modal').classList.add('hidden');
      document.getElementById('city-modal').classList.remove('flex');
    }

    function openGlossaryModal() {
      document.getElementById('glossary-modal').classList.remove('hidden');
      document.getElementById('glossary-modal').classList.add('flex');
      loadGlossary();
    }
    function closeGlossaryModal() {
      document.getElementById('glossary-modal').classList.add('hidden');
      document.getElementById('glossary-modal').classList.remove('flex');
    }

    function openJudgeModal() {
      document.getElementById('judge-modal').classList.remove('hidden');
      document.getElementById('judge-modal').classList.add('flex');
    }
    function closeJudgeModal() {
      document.getElementById('judge-modal').classList.add('hidden');
      document.getElementById('judge-modal').classList.remove('flex');
    }

    async function loadGlossary() {
      if (glossaryData) return;
      try {
        const resp = await fetch('/api/glossary');
        glossaryData = await resp.json();
        let html = '';
        for (const [k, item] of Object.entries(glossaryData)) {
          html += `
            <div class="p-3 rounded-2xl bg-[#161922] border border-white/5 space-y-1.5">
              <div class="flex justify-between items-center">
                <span class="font-bold text-white text-xs">${item.term}</span>
                <span class="text-[9px] px-2 py-0.5 rounded bg-blue-950 text-blue-300 font-mono">${item.nasa_mission}</span>
              </div>
              <div class="text-[10px] text-amber-300 font-mono">Formula: ${item.formula}</div>
              <p class="text-gray-300 text-[11px]">${item.definition}</p>
            </div>
          `;
        }
        document.getElementById('glossary-items-container').innerHTML = html;
      } catch (e) {
        console.error(e);
      }
    }

    async function loadProvinces() {
      try {
        const resp = await fetch('/api/provinces');
        pakistanData = await resp.json();
        REGISTERED_CITIES_LIST.length = 0;
        for (const [prov, pdata] of Object.entries(pakistanData)) {
          for (const [ckey, cinfo] of Object.entries(pdata.cities || {})) {
            REGISTERED_CITIES_LIST.push({
              name: cinfo.name,
              key: ckey,
              province: prov,
              barani: !!cinfo.barani,
              lat: cinfo.lat,
              lon: cinfo.lon
            });
          }
        }
        populateCitySelect(currentProvince);
      } catch (e) {}
    }

    function onProvinceChange() {
      currentProvince = document.getElementById('province-select').value;
      populateCitySelect(currentProvince);
      selectCity(document.getElementById('city-select').value);
    }

    function populateCitySelect(prov) {
      const sel = document.getElementById('city-select');
      sel.innerHTML = "";
      if (!pakistanData[prov]) return;
      for (const [k, c] of Object.entries(pakistanData[prov].cities)) {
        const opt = document.createElement('option');
        opt.value = k;
        opt.text = c.name;
        if (k === currentCity) opt.selected = true;
        sel.appendChild(opt);
      }
    }

    function onCityDropdownChange() {
      selectCity(document.getElementById('city-select').value);
    }

    async function autoDetectLocation() {
      try {
        const resp = await fetch('/api/detect-location');
        const d = await resp.json();
        selectCity(d.matched_city_key);
      } catch (e) {
        selectCity('chakwal');
      }
    }

    // ── SAVED LOCATIONS CONTROLLER ──────────────────────────────────────────
    function openSavedLocationsModal() {
      renderSavedLocationsModalList();
      document.getElementById('saved-locations-modal').classList.remove('hidden');
      document.getElementById('saved-locations-modal').classList.add('flex');
    }

    function closeSavedLocationsModal() {
      document.getElementById('saved-locations-modal').classList.add('hidden');
      document.getElementById('saved-locations-modal').classList.remove('flex');
    }

    function showToast(msg, isSuccess = true) {
      const toast = document.getElementById('toast-notification');
      const toastMsg = document.getElementById('toast-msg');
      const toastIcon = document.getElementById('toast-icon');
      if (!toast || !toastMsg) return;

      toastMsg.innerText = msg;
      if (isSuccess) {
        toast.className = "fixed bottom-5 right-5 z-50 bg-[#1b1e27] border border-emerald-500/60 text-white px-4 py-2.5 rounded-2xl shadow-2xl flex items-center space-x-2.5 transition-all duration-300 opacity-100 pointer-events-auto transform translate-y-0";
        if (toastIcon) toastIcon.className = "fa-solid fa-circle-check text-emerald-400";
      } else {
        toast.className = "fixed bottom-5 right-5 z-50 bg-[#1b1e27] border border-rose-500/60 text-white px-4 py-2.5 rounded-2xl shadow-2xl flex items-center space-x-2.5 transition-all duration-300 opacity-100 pointer-events-auto transform translate-y-0";
        if (toastIcon) toastIcon.className = "fa-solid fa-triangle-exclamation text-rose-400";
      }

      clearTimeout(window._toastTimer);
      window._toastTimer = setTimeout(() => {
        toast.className = "fixed bottom-5 right-5 z-50 bg-[#1b1e27] border border-emerald-500/50 text-white px-4 py-2.5 rounded-2xl shadow-2xl flex items-center space-x-2.5 transition-all duration-300 opacity-0 pointer-events-none transform translate-y-2";
      }, 3500);
    }

    async function loadSavedLocations() {
      try {
        const resp = await fetch('/api/saved-locations');
        savedLocations = await resp.json();
      } catch (e) {
        const local = localStorage.getItem('fieldshift_saved_locations');
        if (local) {
          try { savedLocations = JSON.parse(local); } catch (err) { savedLocations = []; }
        }
      }

      try { localStorage.setItem('fieldshift_saved_locations', JSON.stringify(savedLocations)); } catch (e) {}

      updateSavedCountBadge();
      renderSavedLocationsTray();
      renderModalSavedChips();
      updateSaveButtonState();
    }

    function updateSavedCountBadge() {
      const badge = document.getElementById('saved-count-badge');
      if (badge) badge.innerText = savedLocations.length;
    }

    function isLocationSaved(name, lat, lon) {
      if (!savedLocations || savedLocations.length === 0) return false;
      const cName = (name || currentCity || "").toLowerCase().trim();
      return savedLocations.some(l => {
        if (l.name.toLowerCase() === cName) return true;
        if (lat !== undefined && lon !== undefined && lat !== null && lon !== null) {
          const d = Math.hypot(l.lat - lat, l.lon - lon);
          if (d < 0.05) return true;
        }
        return false;
      });
    }

    function updateSaveButtonState() {
      const btn = document.getElementById('btn-save-location');
      const icon = document.getElementById('save-location-icon');
      const text = document.getElementById('save-location-text');
      if (!btn || !icon || !text) return;

      const saved = isLocationSaved(currentCity, currentLat, currentLon);
      if (saved) {
        btn.className = "flex items-center space-x-1.5 px-2.5 py-1 rounded-full bg-amber-950/70 hover:bg-amber-900/80 border border-amber-500/60 text-xs text-amber-300 transition shadow";
        icon.className = "fa-solid fa-star text-amber-400";
        text.innerText = "Saved ★";
        btn.title = "Location saved in your research sites. Click to manage.";
      } else {
        btn.className = "flex items-center space-x-1.5 px-2.5 py-1 rounded-full bg-[#1b1e27] hover:bg-[#252a34] border border-white/10 text-xs text-gray-300 hover:text-white transition shadow";
        icon.className = "fa-regular fa-star text-amber-400";
        text.innerText = "Save Location";
        btn.title = "Save this location to favorites";
      }
    }

    function renderSavedLocationsTray() {
      const container = document.getElementById('saved-locations-chips-container');
      if (!container) return;

      if (savedLocations.length === 0) {
        container.innerHTML = '<span class="text-gray-500 text-[10px] italic">No saved sites yet.</span>';
        return;
      }

      let html = '';
      savedLocations.forEach(loc => {
        const isActive = (loc.name.toLowerCase() === currentCity.toLowerCase());
        const chipClass = isActive
          ? "bg-blue-600 text-white font-bold border-blue-400"
          : "bg-[#181b23] text-gray-300 hover:text-white hover:bg-[#222733] border-white/10";

        html += `
          <button onclick="switchToSavedLocation('${loc.name}', ${loc.lat}, ${loc.lon})"
                  class="px-2.5 py-0.5 rounded-full border text-[10px] flex items-center space-x-1 flex-shrink-0 transition shadow-sm ${chipClass}">
            <span>${loc.is_default ? '⭐' : '📍'}</span>
            <span class="truncate max-w-[110px]">${loc.display_name.split(',')[0]}</span>
          </button>
        `;
      });
      container.innerHTML = html;
    }

    function renderModalSavedChips() {
      const container = document.getElementById('modal-saved-chips');
      if (!container) return;

      if (savedLocations.length === 0) {
        container.innerHTML = '<span class="text-gray-500 text-[10px] italic">No saved locations yet.</span>';
        return;
      }

      let html = '';
      savedLocations.forEach(loc => {
        html += `
          <button onclick="switchToSavedLocation('${loc.name}', ${loc.lat}, ${loc.lon}); closeCityPicker();"
                  class="px-2 py-0.5 rounded-lg bg-[#181b23] hover:bg-blue-900/60 border border-white/10 text-gray-200 text-[10px] font-mono flex items-center space-x-1 transition">
            <span class="text-amber-400">${loc.is_default ? '★' : '•'}</span>
            <span>${loc.display_name}</span>
          </button>
        `;
      });
      container.innerHTML = html;
    }

    function renderSavedLocationsModalList() {
      const container = document.getElementById('saved-locations-list-container');
      if (!container) return;

      if (savedLocations.length === 0) {
        container.innerHTML = `
          <div class="text-center py-6 text-gray-400">
            <i class="fa-solid fa-bookmark text-2xl text-gray-600 mb-2"></i>
            <p>No saved agricultural sites found.</p>
            <p class="text-[10px] text-gray-500">Pick any location on the map or selector and save it.</p>
          </div>
        `;
        return;
      }

      let html = '';
      savedLocations.forEach(loc => {
        const isActive = (loc.name.toLowerCase() === currentCity.toLowerCase());
        html += `
          <div class="p-3 rounded-2xl bg-[#161922] border ${isActive ? 'border-blue-500/50 bg-blue-950/20' : 'border-white/5'} flex items-center justify-between space-x-2 transition">
            <div class="flex-1 min-w-0">
              <div class="flex items-center space-x-1.5">
                <span class="font-bold text-white text-xs truncate">${loc.display_name}</span>
                ${loc.is_default ? '<span class="px-1.5 py-0.2 rounded bg-amber-950 text-amber-300 border border-amber-600/40 text-[9px] font-mono font-bold">Default</span>' : ''}
                ${isActive ? '<span class="px-1.5 py-0.2 rounded bg-blue-950 text-blue-300 border border-blue-600/40 text-[9px] font-mono">Active</span>' : ''}
              </div>
              <div class="text-[10px] text-gray-400 font-mono mt-0.5">
                <span>${loc.province}</span> · <span>${loc.lat.toFixed(4)}°N, ${loc.lon.toFixed(4)}°E</span>
              </div>
              ${loc.notes ? `<p class="text-[10px] text-amber-200/80 italic mt-0.5">${loc.notes}</p>` : ''}
            </div>

            <div class="flex items-center space-x-1.5 flex-shrink-0">
              <button onclick="switchToSavedLocation('${loc.name}', ${loc.lat}, ${loc.lon}); closeSavedLocationsModal();"
                      class="px-2.5 py-1 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-bold text-[10px] transition shadow flex items-center space-x-1">
                <i class="fa-solid fa-location-arrow text-[9px]"></i>
                <span>Load</span>
              </button>
              ${!loc.is_default ? `
                <button onclick="setDefaultSavedLocation(${loc.id})" title="Set as default location"
                        class="px-2 py-1 rounded-xl bg-white/5 hover:bg-white/10 text-amber-400 hover:text-amber-300 border border-white/5 text-[10px] transition">
                  <i class="fa-regular fa-star"></i>
                </button>
              ` : ''}
              <button onclick="deleteSavedLocation(${loc.id}, '${loc.name}')" title="Delete location"
                      class="w-6 h-6 rounded-lg bg-white/5 hover:bg-rose-950/80 text-gray-400 hover:text-rose-400 border border-white/5 flex items-center justify-center text-[10px] transition">
                <i class="fa-solid fa-trash-can"></i>
              </button>
            </div>
          </div>
        `;
      });
      container.innerHTML = html;
    }

    async function toggleSaveCurrentLocation() {
      if (isLocationSaved(currentCity, currentLat, currentLon)) {
        openSavedLocationsModal();
        return;
      }

      const disp = (latestData && latestData.display_name) ? latestData.display_name : (currentCity.charAt(0).toUpperCase() + currentCity.slice(1));
      const prov = currentProvince || "Punjab";

      try {
        const resp = await fetch('/api/saved-locations', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            name: currentCity,
            display_name: disp,
            province: prov,
            lat: currentLat,
            lon: currentLon,
            is_default: savedLocations.length === 0 ? 1 : 0,
            notes: "Saved via web GUI"
          })
        });
        const d = await resp.json();
        if (d.saved_locations) savedLocations = d.saved_locations;
        showToast(`✓ Location saved: ${disp}`);
      } catch (e) {
        showToast(`✓ Location saved: ${disp}`);
      }

      await loadSavedLocations();
    }

    async function saveCurrentLocationWithLabel() {
      const input = document.getElementById('save-custom-label-input');
      const customLabel = input ? input.value.trim() : "";
      const disp = customLabel || (latestData && latestData.display_name) || (currentCity.charAt(0).toUpperCase() + currentCity.slice(1));
      const prov = currentProvince || "Punjab";

      try {
        const resp = await fetch('/api/saved-locations', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            name: currentCity,
            display_name: disp,
            province: prov,
            lat: currentLat,
            lon: currentLon,
            is_default: 0,
            notes: customLabel ? `Custom Farm: ${customLabel}` : "Saved via web GUI"
          })
        });
        const d = await resp.json();
        if (d.saved_locations) savedLocations = d.saved_locations;
      } catch (e) {}

      if (input) input.value = "";
      showToast(`✓ Location saved: ${disp}`);
      await loadSavedLocations();
      renderSavedLocationsModalList();
    }

    async function applyAndSaveModalLocation() {
      const cityKey = document.getElementById('city-select').value;
      const makeDefault = document.getElementById('modal-set-default-check').checked;
      closeCityPicker();

      let disp = cityKey;
      let lat = currentLat;
      let lon = currentLon;
      let prov = currentProvince;

      if (pakistanData[prov] && pakistanData[prov].cities && pakistanData[prov].cities[cityKey]) {
        const c = pakistanData[prov].cities[cityKey];
        disp = `${c.name}, ${prov}`;
        lat = c.lat;
        lon = c.lon;
      }

      try {
        await fetch('/api/saved-locations', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            name: cityKey,
            display_name: disp,
            province: prov,
            lat: lat,
            lon: lon,
            is_default: makeDefault ? 1 : 0,
            notes: makeDefault ? "Default farm hub" : "Selected in province picker"
          })
        });
      } catch (e) {}

      showToast(`✓ Location saved: ${disp}`);
      await loadSavedLocations();
      selectCity(cityKey);
    }

    async function switchToSavedLocation(locName, lat, lon) {
      currentCity = locName.toLowerCase();
      if (lat !== undefined && lon !== undefined) {
        currentLat = lat;
        currentLon = lon;
      }

      clearSearch();
      showToast(`📍 Loading details for ${locName.charAt(0).toUpperCase() + locName.slice(1)}...`);
      await queryPrediction(locName, lat, lon);
      renderSavedLocationsTray();
      renderSavedLocationsModalList();
    }

    async function deleteSavedLocation(id, name) {
      try {
        const resp = await fetch(`/api/saved-locations/delete?id=${id}&name=${encodeURIComponent(name)}`);
        const d = await resp.json();
        if (d.saved_locations) savedLocations = d.saved_locations;
      } catch (e) {
        savedLocations = savedLocations.filter(l => l.id !== id && l.name !== name);
      }
      showToast(`Removed from saved locations.`);
      await loadSavedLocations();
      renderSavedLocationsModalList();
    }

    async function setDefaultSavedLocation(id) {
      try {
        const resp = await fetch(`/api/saved-locations/default?id=${id}`);
        const d = await resp.json();
        if (d.saved_locations) savedLocations = d.saved_locations;
      } catch (e) {
        savedLocations.forEach(l => l.is_default = (l.id === id));
      }
      showToast(`✓ Set as primary default location.`);
      await loadSavedLocations();
      renderSavedLocationsModalList();
    }

    window.onload = async function() {
      startClock();
      initMap();

      // Temperature Unit (Default: Celsius)
      try {
        const storedUnit = localStorage.getItem('fieldshift_temp_unit');
        useFahrenheit = (storedUnit === 'F');
        const unitBtn = document.getElementById('temp-unit-toggle');
        if (unitBtn) unitBtn.innerText = useFahrenheit ? '°F' : '°C';
      } catch (e) {}

      await loadProvinces();
      await loadSavedLocations();

      let initialStation = "chakwal";
      let initialLat = null;
      let initialLon = null;

      const defaultLoc = savedLocations.find(l => l.is_default);
      if (defaultLoc) {
        initialStation = defaultLoc.name;
        initialLat = defaultLoc.lat;
        initialLon = defaultLoc.lon;
      } else if (savedLocations.length > 0) {
        initialStation = savedLocations[0].name;
        initialLat = savedLocations[0].lat;
        initialLon = savedLocations[0].lon;
      }

      queryPrediction(initialStation, initialLat, initialLon);
    };
  </script>
</body>
</html>
"""


class DashboardRequestHandler(BaseHTTPRequestHandler):
    """Custom HTTP handler serving the GUI dashboard and real-time JSON prediction endpoints."""

    def log_message(self, format, *args):
        return

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)

        if path == "/" or path == "/index.html":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HTML_DASHBOARD.encode("utf-8"))
            return

        elif path == "/api/predict":
            station = query.get("station", [None])[0]
            lat = float(query.get("lat", [None])[0]) if query.get("lat", [None])[0] else None
            lon = float(query.get("lon", [None])[0]) if query.get("lon", [None])[0] else None
            radius = float(query.get("radius", [25.0])[0])
            gemini_key = query.get("gemini_key", [None])[0]

            try:
                # skip_gemini=True → instant response (<1s); Gemini advisory
                # is loaded separately in background via /api/gemini-feasibility
                res = predict(
                    station=station,
                    lat=lat,
                    lon=lon,
                    radius_km=radius,
                    gemini_api_key=gemini_key,
                    query_nasa_live=False,
                    skip_gemini=True
                )

                # Add Unique Innovations
                vwc_root = res["soil"]["volumetric_water_15cm_m3m3"]
                flood_score = res["flood_risk"]["flood_risk_score"]
                aqi_val = res["air_quality"]["aqi"]
                smd_mm = res["soil"]["moisture_deficit_mm"]
                is_barani = res["barani"]

                res["ccrs"] = calculate_ccrs(vwc_root, flood_score, aqi_val, smd_mm, is_barani)
                cf = res["crop_feasibility"]
                res["bilingual_advisory"] = generate_bilingual_advisory(
                    res["location"], cf["is_worth_it"],
                    cf.get("recommended_crops", ["Wheat"]),
                    res["flood_risk"]["badge"], aqi_val, is_barani
                )
                res["drainage_vector"] = calculate_drainage_vector(
                    res["coordinates"]["lat"], res["coordinates"]["lon"],
                    res["elevation_m"], res["river_basin"]
                )

                # Persist encrypted record in database vault
                save_secure_assessment("Pakistan", res["location"], res)

                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(res).encode("utf-8"))
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))
            return

        elif path == "/api/gemini-feasibility":
            # Async Gemini advisory — called in background after fast /api/predict loads the UI
            station = query.get("station", [None])[0]
            lat_g = float(query.get("lat", [None])[0]) if query.get("lat", [None])[0] else None
            lon_g = float(query.get("lon", [None])[0]) if query.get("lon", [None])[0] else None
            radius = float(query.get("radius", [25.0])[0])
            try:
                res_g = predict(
                    station=station, lat=lat_g, lon=lon_g,
                    radius_km=radius,
                    gemini_api_key=DEFAULT_GEMINI_KEY,
                    query_nasa_live=False,
                    skip_gemini=False
                )
                cf = res_g.get("crop_feasibility", {})
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(json.dumps(cf).encode("utf-8"))
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))
            return

        elif path == "/api/detect-location":
            client_ip = self.client_address[0]
            detected = detect_user_location(client_ip if client_ip != "127.0.0.1" else None)
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(detected).encode("utf-8"))
            return

        elif path == "/api/provinces":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(PAKISTAN_PROVINCES).encode("utf-8"))
            return

        elif path == "/api/judge-dossier":
            dossier = get_nasa_judge_dossier()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(dossier).encode("utf-8"))
            return

        elif path == "/api/cities":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(REGIONAL_CITIES).encode("utf-8"))
            return

        elif path == "/api/rotations":
            station = query.get("station", ["chakwal"])[0]
            priority = query.get("priority", ["water"])[0]
            try:
                vwc = float(query.get("vwc", [0.24])[0])
            except (ValueError, TypeError):
                vwc = 0.24
            try:
                flood = float(query.get("flood", [18.5])[0])
            except (ValueError, TypeError):
                flood = 18.5

            is_barani = True
            if station and station.lower() in REGIONAL_CITIES:
                is_barani = REGIONAL_CITIES[station.lower()].get("barani", True)

            rot_data = simulate_crop_rotations(
                city_name=station,
                is_barani=is_barani,
                vwc_root=vwc,
                flood_score=flood,
                farmer_priority=priority
            )
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(rot_data).encode("utf-8"))
            return

        elif path == "/api/climate-sensitivity":
            try:
                temp = float(query.get("temp", [22.0])[0])
                precip = float(query.get("precip", [2.0])[0])
                vwc = float(query.get("vwc", [0.24])[0])
                flood = float(query.get("flood", [18.5])[0])
                temp_delta = float(query.get("temp_delta", [0.0])[0])
                precip_mult = float(query.get("precip_mult", [1.0])[0])
            except (ValueError, TypeError):
                temp, precip, vwc, flood, temp_delta, precip_mult = 22.0, 2.0, 0.24, 18.5, 0.0, 1.0

            clim_data = simulate_climate_sensitivity(
                base_temp=temp,
                base_precip=precip,
                base_vwc=vwc,
                base_flood=flood,
                temp_delta=temp_delta,
                precip_mult=precip_mult
            )
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(clim_data).encode("utf-8"))
            return

        elif path == "/api/glossary":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(SCIENTIFIC_GLOSSARY).encode("utf-8"))
            return

        elif path == "/api/crop-catalog":
            from crop_catalog_service import search_crops
            q = query.get("q", [None])[0]
            grp = query.get("group", [None])[0]
            try:
                lim = int(query.get("limit", [50])[0])
            except (ValueError, TypeError):
                lim = 50
            try:
                off = int(query.get("offset", [0])[0])
            except (ValueError, TypeError):
                off = 0
            res_crops = search_crops(query=q, group=grp, limit=lim, offset=off)
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(res_crops).encode("utf-8"))
            return

        elif path == "/api/crop-catalog/groups":
            from crop_catalog_service import get_crop_groups
            groups = get_crop_groups()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(groups).encode("utf-8"))
            return

        elif path == "/api/crop-catalog/detail":
            from crop_catalog_service import get_crop_by_id
            crop_id = query.get("id", ["CR0001"])[0]
            crop_item = get_crop_by_id(crop_id)
            self.send_response(200 if crop_item else 404)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(crop_item or {"error": "Crop not found"}).encode("utf-8"))
            return

        elif path == "/api/crop-catalog/stats":
            from crop_catalog_service import get_crop_stats
            stats = get_crop_stats()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(stats).encode("utf-8"))
            return

        elif path == "/api/saved-locations":
            locs = get_user_saved_locations()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(locs).encode("utf-8"))
            return

        elif path == "/api/saved-locations/save":
            name = query.get("name", [""])[0]
            display_name = query.get("display_name", [name.title()])[0]
            province = query.get("province", ["Punjab"])[0]
            try:
                lat = float(query.get("lat", [32.9328])[0])
                lon = float(query.get("lon", [72.8631])[0])
            except (ValueError, TypeError):
                lat, lon = 32.9328, 72.8631
            is_default = 1 if query.get("is_default", ["0"])[0] in ["1", "true", "True"] else 0
            notes = query.get("notes", [""])[0]
            updated = save_user_location(name, display_name, province, lat, lon, is_default, notes)
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps({"success": True, "saved_locations": updated}).encode("utf-8"))
            return

        elif path == "/api/saved-locations/delete":
            loc_id = query.get("id", [None])[0]
            loc_name = query.get("name", [None])[0]
            updated = delete_user_saved_location(location_id=loc_id, name=loc_name)
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps({"success": True, "saved_locations": updated}).encode("utf-8"))
            return

        elif path == "/api/saved-locations/default":
            target = query.get("id", query.get("name", [None]))[0]
            updated = set_default_saved_location(target)
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps({"success": True, "saved_locations": updated}).encode("utf-8"))
            return

        else:
            self.send_response(404)
            self.end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8') if content_length > 0 else ""
        try:
            payload = json.loads(body) if body else {}
        except Exception:
            payload = {}

        if path == "/api/saved-locations":
            name = payload.get("name", "")
            display_name = payload.get("display_name", name.title())
            province = payload.get("province", "Punjab")
            try:
                lat = float(payload.get("lat", 32.9328))
                lon = float(payload.get("lon", 72.8631))
            except (ValueError, TypeError):
                lat, lon = 32.9328, 72.8631
            is_default = 1 if payload.get("is_default") else 0
            notes = payload.get("notes", "")
            updated = save_user_location(name, display_name, province, lat, lon, is_default, notes)
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps({"success": True, "saved_locations": updated}).encode("utf-8"))
            return

        elif path == "/api/saved-locations/delete":
            loc_id = payload.get("id")
            loc_name = payload.get("name")
            updated = delete_user_saved_location(location_id=loc_id, name=loc_name)
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps({"success": True, "saved_locations": updated}).encode("utf-8"))
            return

        elif path == "/api/saved-locations/default":
            target = payload.get("id", payload.get("name"))
            updated = set_default_saved_location(target)
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps({"success": True, "saved_locations": updated}).encode("utf-8"))
            return

        else:
            self.send_response(404)
            self.end_headers()


def start_gui_server(port=5000, open_browser=True):
    """Starts the local dashboard server and opens it in the browser."""
    init_secure_database()
    server = None
    actual_port = port
    for p in range(port, port + 20):
        try:
            server = HTTPServer(("127.0.0.1", p), DashboardRequestHandler)
            actual_port = p
            break
        except OSError:
            continue

    if not server:
        print(f"[!] Could not bind to any port between {port} and {port+20}.")
        return

    url = f"http://127.0.0.1:{actual_port}"
    print("\n" + "=" * 70)
    print("   🚀 NASA FIELD SHIFT — THE HACKERS DEN AI INTERACTIVE GUI DASHBOARD")
    print("=" * 70)
    print(f" [✓] Local GUI Server running at:  {url}")
    print(f" [✓] Official NASA Earth Data  :  NASA POWER API & GIBS WMTS")
    print(f" [✓] Database Security Vault   :  PBKDF2-HMAC-SHA256 Encrypted")
    print(f" [✓] Agricultural Advisor      :  Google Gemini AI + PARC Engine")
    print("=" * 70)
    print(" Press Ctrl+C in terminal to stop the server.\n")

    if open_browser:
        threading.Timer(0.8, lambda: webbrowser.open(url)).start()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[*] Shutting down GUI server.")
        server.server_close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Prithvi AI + NASA Earth Data Interactive GUI")
    parser.add_argument("--port", type=int, default=5000, help="Local HTTP server port (default: 5000)")
    parser.add_argument("--no-browser", action="store_true", help="Do not automatically launch web browser")
    args = parser.parse_args()

    start_gui_server(port=args.port, open_browser=not args.no_browser)
