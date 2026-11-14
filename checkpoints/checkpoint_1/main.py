"""
NASA Field Shift — Unified Master Launcher & Guided Agricultural Wizard
========================================================================
Interactive guided wizard asking:
  1. Pakistan State / Province
  2. City / Tehsil (with automated GPS / Network Geolocation API option)
  3. Forecast Date Range
  4. Area Range (5 km to 100 km farm scan radius)

Secured via Military-Grade PBKDF2-HMAC-SHA256 Encrypted Database Vault.
Integrated with IBM-NASA Prithvi EO-V2 300M, NASA POWER API, Flood Hydrology,
and Google Gemini AI Agricultural Land & Crop Feasibility Doctor.
"""

import os
import sys
import time
from datetime import datetime, timedelta

script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

from location_service import (
    PAKISTAN_PROVINCES,
    detect_user_location,
    find_closest_pakistan_city
)
from security_vault import (
    init_secure_database,
    create_security_session,
    save_secure_assessment,
    log_security_event,
    load_secure_api_key
)
from predict_soil_weather import predict, print_full_dashboard
from nasa_hackathon_innovations import (
    calculate_ccrs,
    generate_bilingual_advisory,
    calculate_drainage_vector,
    get_nasa_judge_dossier
)


def clear_banner():
    print("\n" + "=" * 75)
    print(" 🛰️  NASA SPACE APPS HACKATHON 2026 — PRITHVI AI AGRO-CLIMATIC SYSTEM")
    print("     NASA-IBM Prithvi EO-V2 300M · NASA POWER API · Flood Hydrology")
    print("=" * 75)


def run_interactive_wizard():
    clear_banner()
    
    # ── STEP 0: INITIALIZE CRYPTOGRAPHIC DATABASE VAULT ────────────────────────
    print("[*] Initializing Military-Grade PBKDF2-HMAC-SHA256 Database Vault...")
    init_secure_database()
    token, s_id = create_security_session("Agronomist", "CLI-Operator")
    print(f"[✓] Encrypted Database Vault Online. Session ID: {s_id[:12]}...")
    print(f"[✓] Anti-Tamper Integrity: HMAC-SHA256 Hardware-Bound Protection Active\n")
    
    # ── STEP 1: AUTOMATED LOCATION ACCESS API OPTION ───────────────────────────
    print("─" * 75)
    print("📍 LOCATION ACCESS OPTIONS:")
    print("   [1] Auto-Detect my Location via Network Geolocation API")
    print("   [2] Manually select State/Province and City from Pakistan")
    print("   [3] Enter custom GPS Coordinates (Latitude, Longitude)")
    print("─" * 75)
    
    loc_choice = input("Enter choice [1/2/3, default=1]: ").strip() or "1"
    
    selected_city_key = "chakwal"
    selected_province = "Punjab"
    custom_lat = None
    custom_lon = None
    
    if loc_choice == "1":
        print("\n[*] Querying Location Access API ...", end="", flush=True)
        detected = detect_user_location()
        print(f" Detected: {detected['source']}")
        print(f" [+] Nearest Agricultural Center: {detected['matched_city_name']} ({detected['matched_province']})")
        print(f" [+] Agro-Zone: {detected['zone']} | River Basin: {detected['river_basin']}")
        print(f" [+] Coordinates: {detected['detected_lat']}°N, {detected['detected_lon']}°E\n")
        
        confirm = input(f"Proceed with {detected['matched_city_name']}, {detected['matched_province']}? [Y/n]: ").strip().lower()
        if confirm != "n":
            selected_city_key = detected["matched_city_key"]
            selected_province = detected["matched_province"]
            custom_lat = detected["detected_lat"]
            custom_lon = detected["detected_lon"]
        else:
            loc_choice = "2"
            
    if loc_choice == "2":
        # ── Cascading State / Province Selector ───────────────────────────────
        print("\n" + "─" * 75)
        print("🇵🇰 SELECT YOUR STATE / PROVINCE FROM PAKISTAN:")
        print("─" * 75)
        provinces = list(PAKISTAN_PROVINCES.keys())
        for idx, prov in enumerate(provinces, 1):
            desc = PAKISTAN_PROVINCES[prov]["display"]
            print(f"  [{idx}] {desc}")
            
        prov_idx = input(f"\nSelect Province (1-{len(provinces)}) [default=1 for Punjab]: ").strip() or "1"
        try:
            prov_num = int(prov_idx)
            if 1 <= prov_num <= len(provinces):
                selected_province = provinces[prov_num - 1]
            else:
                selected_province = "Punjab"
        except ValueError:
            selected_province = "Punjab"
            
        print(f"\n[+] Selected Province: {selected_province}")
        
        # ── Cascading City / Tehsil Selector ──────────────────────────────────
        city_dict = PAKISTAN_PROVINCES[selected_province]["cities"]
        city_keys = list(city_dict.keys())
        
        print("\n" + "─" * 75)
        print(f"🏙️  SELECT CITY / TEHSIL IN {selected_province.upper()}:")
        print("─" * 75)
        for idx, c_key in enumerate(city_keys, 1):
            c_info = city_dict[c_key]
            barani_tag = "🌾 Barani (Rainfed)" if c_info["barani"] else "🚜 Canal Irrigated"
            print(f"  [{idx:2d}] {c_info['name']:<14} | {c_info['zone']:<28} | {barani_tag}")
            
        city_idx = input(f"\nSelect City (1-{len(city_keys)}) [default=1 for {city_dict[city_keys[0]]['name']}]: ").strip() or "1"
        try:
            c_num = int(city_idx)
            if 1 <= c_num <= len(city_keys):
                selected_city_key = city_keys[c_num - 1]
            else:
                selected_city_key = city_keys[0]
        except ValueError:
            selected_city_key = city_keys[0]
            
        print(f"[+] Selected Location: {city_dict[selected_city_key]['name']}")
        
    elif loc_choice == "3":
        print("\n" + "─" * 75)
        print("📍 ENTER CUSTOM GPS COORDINATES:")
        print("─" * 75)
        lat_in = input("Enter Latitude (e.g. 32.9328): ").strip() or "32.9328"
        lon_in = input("Enter Longitude (e.g. 72.8631): ").strip() or "72.8631"
        custom_lat = float(lat_in)
        custom_lon = float(lon_in)
        closest = find_closest_pakistan_city(custom_lat, custom_lon)
        selected_province = closest["province"]
        selected_city_key = closest["city_key"]
        print(f"[+] Custom coordinates matched near {closest['city']['name']}, {selected_province}")

    # ── STEP 2: DATE RANGE SELECTION ───────────────────────────────────────────
    print("\n" + "─" * 75)
    print("📅 WHAT DATA / FORECAST DATE RANGE DO YOU WANT?")
    print("─" * 75)
    print("   [1] Real-Time Satellite Telemetry & Immediate Inundation (Today)")
    print("   [2] 24-Hour Flash Flood & Soil Saturation Window")
    print("   [3] 7-Day Farm Management Outlook (Recommended)")
    print("   [4] 14-Day Planting & Phenological Cycle")
    print("   [5] Seasonal Rabi/Kharif Window (30-Day Outlook)")
    
    date_choice = input("\nEnter Date Range [1-5, default=1]: ").strip() or "1"
    now = datetime.utcnow()
    
    date_offsets = {
        "1": timedelta(hours=0),
        "2": timedelta(days=1),
        "3": timedelta(days=7),
        "4": timedelta(days=14),
        "5": timedelta(days=30),
    }
    target_dt = now + date_offsets.get(date_choice, timedelta(hours=0))
    target_time_str = target_dt.strftime("%Y-%m-%d %H:%M:%S")
    print(f"[+] Target Forecast Time: {target_time_str} UTC")

    # ── STEP 3: AREA RANGE (SCAN RADIUS) SELECTION ─────────────────────────────
    print("\n" + "─" * 75)
    print("🧭 WHAT AREA RANGE (SURROUNDING FARM PERIMETER) DO YOU WANT?")
    print("─" * 75)
    print("   [1]  5 km  (Farm Boundary & Immediate Fields)")
    print("   [2] 10 km  (Village & Local Mauza Cluster)")
    print("   [3] 25 km  (Tehsil & Agricultural District) [Recommended]")
    print("   [4] 50 km  (Sub-Catchment Watershed)")
    print("   [5] 100 km (Regional River Basin & Plain)")
    
    radius_choice = input("\nEnter Area Range [1-5, default=3 for 25km]: ").strip() or "3"
    radius_map = {"1": 5.0, "2": 10.0, "3": 25.0, "4": 50.0, "5": 100.0}
    selected_radius_km = radius_map.get(radius_choice, 25.0)
    print(f"[+] Selected Area Range: {selected_radius_km} km radius")

    # ── STEP 4: GOOGLE GEMINI API KEY CONFIGURATION ────────────────────────────
    vault_gemini_key = load_secure_api_key("gemini")
    gemini_key = vault_gemini_key or os.environ.get("GEMINI_API_KEY", "")
    
    if not gemini_key:
        print("\n" + "─" * 75)
        print("🤖 GOOGLE GEMINI AI CONFIGURATION (Optional):")
        print("─" * 75)
        key_in = input("Enter Google Gemini API Key (or press Enter to use Offline PARC Engine): ").strip()
        if key_in:
            gemini_key = key_in
            save_prompt = input("Encrypt and save this API key securely in the database vault? [Y/n]: ").strip().lower()
            if save_prompt != "n":
                from security_vault import store_secure_api_key
                store_secure_api_key("gemini", key_in)
                print("[✓] Gemini API Key encrypted with AES-256 equivalent and saved in vault.")

    # ── STEP 5: RUN MULTI-MODAL PREDICTION ENGINE ──────────────────────────────
    print("\n" + "=" * 75)
    print(" [*] Executing Prithvi EO-V2 Multi-Task AI & NASA POWER Telemetry Engine...")
    print("=" * 75)
    
    res = predict(
        station=selected_city_key,
        lat=custom_lat,
        lon=custom_lon,
        target_time=target_time_str,
        radius_km=selected_radius_km,
        gemini_api_key=gemini_key,
        query_nasa_live=True
    )
    
    # ── STEP 6: COMPUTE UNIQUE HACKATHON INNOVATIONS ───────────────────────────
    vwc_root = res["soil"]["volumetric_water_15cm_m3m3"]
    flood_score = res["flood_risk"]["flood_risk_score"]
    aqi_val = res["air_quality"]["aqi"]
    smd_mm = res["soil"]["moisture_deficit_mm"]
    is_barani = res["barani"]
    
    # 1. CCRS Score
    ccrs = calculate_ccrs(vwc_root, flood_score, aqi_val, smd_mm, is_barani)
    res["ccrs"] = ccrs
    
    # 2. Bilingual Audio Advisory
    cf = res["crop_feasibility"]
    bilingual = generate_bilingual_advisory(
        res["location"], cf["is_worth_it"],
        cf.get("recommended_crops", ["Wheat"]),
        res["flood_risk"]["badge"], aqi_val, is_barani
    )
    res["bilingual_advisory"] = bilingual
    
    # 3. Drainage Vector
    drainage = calculate_drainage_vector(res["coordinates"]["lat"], res["coordinates"]["lon"], res["elevation_m"], res["river_basin"])
    res["drainage_vector"] = drainage

    # 4. Official NASA Challenge Crop Rotation Strategy Simulation
    from nasa_challenge_evaluator import simulate_crop_rotations
    farmer_pref = "water" if is_barani else "income"
    rotations = simulate_crop_rotations(
        city_name=res["location"],
        is_barani=is_barani,
        vwc_root=vwc_root,
        flood_score=flood_score,
        farmer_priority=farmer_pref
    )
    res["crop_rotations"] = rotations
    
    # ── STEP 7: ENCRYPT AND PERSIST IN VAULT ───────────────────────────────────
    record_hash = save_secure_assessment(selected_province, res["location"], res)
    
    # ── STEP 8: DISPLAY RICH MISSION DOSSIER ───────────────────────────────────
    print_full_dashboard(res)
    
    # Print Unique Hackathon Features Banner
    print("=" * 75)
    print(f" 🏆 NASA SPACE APPS HACKATHON UNIQUE INNOVATIONS:")
    print("=" * 75)
    print(f"  • Crop-Climate Resilience Score (CCRS) : Grade [{ccrs['grade']}] ({ccrs['ccrs_score']}/100) — {ccrs['status']}")
    print(f"    Limiting Factor                      : {ccrs['limiting_factor']}")
    print(f"    Adaptation Strategy                  : {ccrs['adaptation_strategy']}")
    print(f"  • Hydrological Drainage Escape Vector  : {drainage['recommended_drainage_escape']} (Slope: {drainage['slope_gradient_pct']}%)")
    print(f"  • Cryptographic Database Vault Hash    : SHA-256:{record_hash}")
    print("-" * 75)
    print(f" 🔄 NASA DATA-HARMONIZED CROP ROTATION STRATEGY (Field Shift Engine):")
    print(f"  • Recommended Strategy                 : {rotations['recommended_rotation']}")
    print(f"  • Core Strategic Goal                  : {rotations['top_rotation_focus']}")
    for sc in rotations["scenarios"][:2]:
        badge = "⭐ FARMER TOP PICK" if sc.get("is_farmer_top_pick") else "   VIABLE ALTERNATIVE"
        print(f"    [{badge}] {sc['name']} (Suitability Score: {sc['dynamic_score']}/100)")
        cycle_str = " -> ".join(f"{c['crop']} ({c['season']})" for c in sc["cycle"])
        print(f"           Succession : {cycle_str}")
        print(f"           Benefits   : Water Saved: {sc['benefits']['water_savings_pct']}%, N-Fixed: {sc['benefits']['soil_nitrogen_fixed_kg_ha']} kg/ha, Erosion: -{sc['benefits']['erosion_reduction_pct']}%")
    print("-" * 75)
    print("  • 🇵🇰 BILINGUAL FARMER AUDIO BROADCAST (URDU):")
    print(f"    \"{bilingual['urdu']}\"")
    print("-" * 75)
    print("  💡 FARMER EMPOWERMENT NOTICE:")
    print("     NASA Field Shift AI is designed to support and augment—not replace—local")
    print("     farmer wisdom, field inspection, and provincial agricultural extension officers.")
    print("=" * 75)
    
    # Offer to open modern GUI
    print("\nWould you like to launch the Interactive NASA Satellite GUI Dashboard now?")
    gui_launch = input("Launch Modern GUI? [Y/n]: ").strip().lower()
    if gui_launch != "n":
        from prithvi_weather_gui import start_gui_server
        start_gui_server(port=5000, open_browser=True)


if __name__ == "__main__":
    run_interactive_wizard()
