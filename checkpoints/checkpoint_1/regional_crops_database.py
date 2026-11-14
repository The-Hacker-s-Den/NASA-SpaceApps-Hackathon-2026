"""
Regional Pakistan Agricultural Crops Database
==============================================
Comprehensive agronomic crop profiles, varietal recommendations, soil constraints,
and water requirements for agricultural districts across Pakistan.
"""

REGIONAL_CROPS_DATA = {
    "lahore": {
        "zone": "Central Punjab Alluvial Canal Plains (Rice-Wheat Belt)",
        "soil_type": "Rich Silt Loam & Fine Alluvial Clay (pH 7.8 - 8.2)",
        "irrigation": "Canal (BRB / Upper Chenab) + Electric Tubewell",
        "kharif_crops": [
            {"crop": "Super Basmati Rice", "variety": "Kisan Basmati / Super Gold", "sowing": "May 20 - Jun 25", "water_need": "900 - 1100 mm (Standing water)", "yield": "38 - 45 maunds/acre", "gross_margin": "Rs. 140,000 - 180,000/acre"},
            {"crop": "Hybrid Corn (Maize)", "variety": "DK-6789 / Pioneer 30Y87", "sowing": "Jul 15 - Aug 10", "water_need": "450 - 550 mm", "yield": "85 - 110 maunds/acre", "gross_margin": "Rs. 130,000 - 165,000/acre"},
            {"crop": "Fodder Maize / Sorghum", "variety": "Sada Bahar / Hegari", "sowing": "Jun - Jul", "water_need": "300 - 400 mm", "yield": "450 - 600 maunds/acre", "gross_margin": "Rs. 85,000/acre"}
        ],
        "rabi_crops": [
            {"crop": "Grain Wheat", "variety": "Akbar-2019 / Dilkash-2020", "sowing": "Nov 01 - Nov 20", "water_need": "350 - 400 mm (4-5 irrigations)", "yield": "48 - 58 maunds/acre", "gross_margin": "Rs. 120,000 - 150,000/acre"},
            {"crop": "Autumn Potato", "variety": "Mozika / Kuroda / Cardinal", "sowing": "Oct 01 - Oct 20", "water_need": "400 - 500 mm (Light frequent)", "yield": "250 - 320 bags/acre", "gross_margin": "Rs. 250,000 - 380,000/acre"},
            {"crop": "Canola / Raya", "variety": "Super Canola / Khanpur Raya", "sowing": "Oct 15 - Nov 10", "water_need": "200 - 250 mm", "yield": "22 - 28 maunds/acre", "gross_margin": "Rs. 95,000/acre"}
        ],
        "cash_crops": ["Off-season Vegetables", "Guava Orchards", "Strawberry Tunnels"],
        "soil_action": "Incorporate green manure (Sesbania) post-wheat harvest to break rice plow-pan."
    },

    "chakwal": {
        "zone": "Pothohar Plateau (High-Value Semi-Arid Barani Tract)",
        "soil_type": "Sandy Loam to Gravelly Loam, Low Organic Matter (0.45% OM, pH 7.6)",
        "irrigation": "100% Rainfed (Dependent on Monsoon & Winter Westerlies)",
        "kharif_crops": [
            {"crop": "Groundnut (Peanut)", "variety": "Bari-2016 / Golden", "sowing": "Apr 15 - May 20", "water_need": "350 - 450 mm (Rainfed)", "yield": "22 - 32 maunds/acre", "gross_margin": "Rs. 160,000 - 210,000/acre"},
            {"crop": "Pearl Millet (Bajra)", "variety": "MB-87 / Uni-Bajra", "sowing": "Jul 01 - Jul 25", "water_need": "250 - 300 mm", "yield": "25 - 35 maunds/acre", "gross_margin": "Rs. 60,000/acre"},
            {"crop": "Mungbean (Pulse)", "variety": "Chakwal Mung-2006", "sowing": "Jul 05 - Jul 30", "water_need": "200 - 250 mm", "yield": "12 - 18 maunds/acre", "gross_margin": "Rs. 90,000/acre"}
        ],
        "rabi_crops": [
            {"crop": "Rainfed Wheat", "variety": "Chakwal-50 / Markaz-19 / Fateh-20", "sowing": "Oct 20 - Nov 15", "water_need": "250 - 300 mm (Conserve residual monsoon moisture)", "yield": "28 - 42 maunds/acre", "gross_margin": "Rs. 95,000 - 130,000/acre"},
            {"crop": "Desi Chickpea (Gram)", "variety": "Bittal-98 / Balkassar-2000", "sowing": "Oct 10 - Nov 10", "water_need": "180 - 220 mm", "yield": "15 - 22 maunds/acre", "gross_margin": "Rs. 110,000/acre"},
            {"crop": "Mustard / Taramira", "variety": "Chakwal Sarson / Taramira-03", "sowing": "Sep 20 - Oct 15", "water_need": "150 - 200 mm", "yield": "14 - 18 maunds/acre", "gross_margin": "Rs. 75,000/acre"}
        ],
        "cash_crops": ["High-Density Olive Orchards (Bari Zaitoon 1 & 2)", "Grapes (King's Ruby)", "Pistachio"],
        "soil_action": "Deep chisel ploughing before monsoon to store rainfall in root zone. Mulch wheat stubbles."
    },

    "kharian": {
        "zone": "Upper Barani & Tubewell Transition Tract (Gujrat District)",
        "soil_type": "Sandy Silt Loam, Moderate Infiltration (pH 7.7)",
        "irrigation": "Sub-surface Aquifer Solar Tubewell + Supplemental Rainfall",
        "kharif_crops": [
            {"crop": "Groundnut / Pulse Mix", "variety": "Bari-2016", "sowing": "May 01 - May 25", "water_need": "380 mm", "yield": "24 - 30 maunds/acre", "gross_margin": "Rs. 170,000/acre"},
            {"crop": "Hybrid Fodder Corn", "variety": "Pioneer 30Y87", "sowing": "Jul 10 - Aug 05", "water_need": "400 mm", "yield": "75 - 90 maunds/acre", "gross_margin": "Rs. 125,000/acre"},
            {"crop": "Sesame (Til)", "variety": "TH-6 / Til-18", "sowing": "Jun 20 - Jul 15", "water_need": "200 mm", "yield": "8 - 12 maunds/acre", "gross_margin": "Rs. 115,000/acre"}
        ],
        "rabi_crops": [
            {"crop": "Semi-Barani Wheat", "variety": "Akbar-2019 / Chakwal-50", "sowing": "Nov 01 - Nov 20", "water_need": "300 mm (2 tubewell waterings)", "yield": "38 - 48 maunds/acre", "gross_margin": "Rs. 115,000/acre"},
            {"crop": "Canola Oilseed", "variety": "Super Canola", "sowing": "Oct 15 - Nov 05", "water_need": "220 mm", "yield": "20 - 25 maunds/acre", "gross_margin": "Rs. 90,000/acre"},
            {"crop": "Fodder Berseem", "variety": "Agri-Berseem", "sowing": "Oct 01 - Oct 25", "water_need": "400 mm (Frequent cuts)", "yield": "600 - 800 maunds/acre", "gross_margin": "Rs. 100,000/acre"}
        ],
        "cash_crops": ["Citrus Orchards (Kinnow / Musambi)", "Olive Parcels", "Dairy Fodder"],
        "soil_action": "Laser land leveling and solar drip irrigation for orchards to optimize groundwater use."
    },

    "multan": {
        "zone": "Southern Punjab Arid Alluvial Belt (Cotton-Wheat & Mango Zone)",
        "soil_type": "Deep Calcareous Silt Loam & Fine Sandy Loam (pH 8.1 - 8.4)",
        "irrigation": "Canal (Sidhnai / Multan Canals) + Deep Diesel/Electric Tubewell",
        "kharif_crops": [
            {"crop": "BT Cotton", "variety": "CKC-3 / FH-142 / BS-15", "sowing": "Apr 15 - May 31", "water_need": "650 - 750 mm (5-6 irrigations)", "yield": "32 - 42 maunds/acre", "gross_margin": "Rs. 180,000 - 240,000/acre"},
            {"crop": "Sesame (White Til)", "variety": "Til-18 / TS-5", "sowing": "Jun 15 - Jul 15", "water_need": "220 - 280 mm", "yield": "9 - 14 maunds/acre", "gross_margin": "Rs. 135,000/acre"},
            {"crop": "Fodder Jowar / Guara", "variety": "BR-90", "sowing": "Jun - Jul", "water_need": "300 mm", "yield": "400 maunds/acre", "gross_margin": "Rs. 70,000/acre"}
        ],
        "rabi_crops": [
            {"crop": "Wheat (Post-Cotton)", "variety": "Fakhar-e-Bhakkar / Ghazi-2019", "sowing": "Nov 20 - Dec 15", "water_need": "320 - 380 mm", "yield": "42 - 52 maunds/acre", "gross_margin": "Rs. 110,000 - 145,000/acre"},
            {"crop": "Sunflower (Spring)", "variety": "Hysun-33 / NK-278", "sowing": "Jan 15 - Feb 15", "water_need": "350 mm", "yield": "25 - 32 maunds/acre", "gross_margin": "Rs. 120,000/acre"},
            {"crop": "Mustard / Raya", "variety": "Khanpur Raya", "sowing": "Oct 15 - Nov 10", "water_need": "200 mm", "yield": "20 - 26 maunds/acre", "gross_margin": "Rs. 85,000/acre"}
        ],
        "cash_crops": ["World-Class Mango Orchards (Chaunsa, Anwar Ratol, Sindhri)", "Red Chillies", "Early Melon"],
        "soil_action": "Apply gypsum to neutralize sodium hazards in brackish tubewell water. Use ridge-furrow planting."
    },

    "gujranwala": {
        "zone": "Upper Rechna Doab (Core Rice-Wheat & Cash Vegetable Bowl)",
        "soil_type": "Clayey Alluvial Silt Loam, High Water Retention (pH 7.9)",
        "irrigation": "Upper Chenab Canal + Low Salinity Groundwater",
        "kharif_crops": [
            {"crop": "Super Basmati Rice", "variety": "Super Basmati / PK-1121", "sowing": "Jun 01 - Jun 30", "water_need": "950 mm", "yield": "40 - 48 maunds/acre", "gross_margin": "Rs. 165,000 - 210,000/acre"},
            {"crop": "Hybrid Corn (Grain)", "variety": "DK-6789", "sowing": "Jul 20 - Aug 10", "water_need": "480 mm", "yield": "90 - 115 maunds/acre", "gross_margin": "Rs. 140,000/acre"}
        ],
        "rabi_crops": [
            {"crop": "Bread Wheat", "variety": "Akbar-2019 / Subhani-21", "sowing": "Nov 05 - Nov 25", "water_need": "350 mm", "yield": "50 - 60 maunds/acre", "gross_margin": "Rs. 130,000/acre"},
            {"crop": "Autumn Potato", "variety": "Mozika / Kuroda", "sowing": "Oct 01 - Oct 25", "water_need": "450 mm", "yield": "280 - 340 bags/acre", "gross_margin": "Rs. 280,000/acre"}
        ],
        "cash_crops": ["Autumn Cauliflower", "Peas", "High-Value Guava"],
        "soil_action": "Subsoiling every 3 years to shatter compaction pan created by puddling rice."
    },

    "gujrat": {
        "zone": "Chenab-Jhelum Doab (Mixed Irrigated & Hill Torrent Plain)",
        "soil_type": "Sandy Clay Loam with Rich River Silt (pH 7.8)",
        "irrigation": "Upper Jhelum Canal + Tubewell",
        "kharif_crops": [
            {"crop": "Basmati Rice", "variety": "Kisan Basmati / Chenab Basmati", "sowing": "Jun 05 - Jul 05", "water_need": "900 mm", "yield": "38 - 44 maunds/acre", "gross_margin": "Rs. 150,000/acre"},
            {"crop": "Sorghum / Maize Fodder", "variety": "JS-2002", "sowing": "Jun - Jul", "water_need": "320 mm", "yield": "450 maunds/acre", "gross_margin": "Rs. 80,000/acre"}
        ],
        "rabi_crops": [
            {"crop": "Wheat", "variety": "Akbar-2019 / Dilkash-2020", "sowing": "Nov 01 - Nov 20", "water_need": "340 mm", "yield": "45 - 55 maunds/acre", "gross_margin": "Rs. 120,000/acre"},
            {"crop": "Oilseed Canola", "variety": "Super Canola", "sowing": "Oct 15 - Nov 10", "water_need": "220 mm", "yield": "22 - 27 maunds/acre", "gross_margin": "Rs. 95,000/acre"}
        ],
        "cash_crops": ["Citrus Orchards", "Autumn Vegetables", "Turmeric"],
        "soil_action": "Maintain drainage furrows to prevent ponding from Chenab backwater."
    },

    "lalamusa": {
        "zone": "Central Gujrat District Semi-Barani Agricultural Pocket",
        "soil_type": "Loamy Sand to Silt Loam, High Permeability (pH 7.7)",
        "irrigation": "Tubewell + Seasonal Rainfall",
        "kharif_crops": [
            {"crop": "Fodder Corn / Sorghum", "variety": "Sada Bahar", "sowing": "Jun 15 - Jul 20", "water_need": "350 mm", "yield": "480 maunds/acre", "gross_margin": "Rs. 90,000/acre"},
            {"crop": "Sesame / Pulses", "variety": "Til-18", "sowing": "Jul 01 - Jul 25", "water_need": "220 mm", "yield": "10 maunds/acre", "gross_margin": "Rs. 110,000/acre"}
        ],
        "rabi_crops": [
            {"crop": "Wheat", "variety": "Akbar-2019 / Chakwal-50", "sowing": "Nov 05 - Nov 25", "water_need": "320 mm", "yield": "40 - 50 maunds/acre", "gross_margin": "Rs. 115,000/acre"},
            {"crop": "Barseem Fodder", "variety": "Meskawi", "sowing": "Oct 05 - Oct 30", "water_need": "420 mm", "yield": "700 maunds/acre", "gross_margin": "Rs. 105,000/acre"}
        ],
        "cash_crops": ["Potato", "Citrus", "Vegetable Nurseries"],
        "soil_action": "Apply organic compost to improve soil moisture retention."
    },

    "murree": {
        "zone": "Sub-Himalayan Moist Temperate Highland (Mountain Terraces)",
        "soil_type": "Gravelly Brown Forest Soils, High Organic Matter (1.2% OM, pH 6.8 - 7.2)",
        "irrigation": "Natural Mountain Springs + High Rainfall (1200+ mm/year)",
        "kharif_crops": [
            {"crop": "Mountain Sweet Corn", "variety": "Local Highland White / Hybrid", "sowing": "Apr 15 - May 15", "water_need": "Rainfed", "yield": "35 - 45 maunds/acre", "gross_margin": "Rs. 95,000/acre"},
            {"crop": "Off-Season Summer Tomato", "variety": "Roma / Sahil", "sowing": "May 01 - Jun 10", "water_need": "Rainfed + Spring Drip", "yield": "350 - 500 crates/acre", "gross_margin": "Rs. 320,000/acre"}
        ],
        "rabi_crops": [
            {"crop": "Highland Barley / Winter Rye", "variety": "Local Winter", "sowing": "Oct 15 - Nov 10", "water_need": "Rainfed / Snowmelt", "yield": "20 - 25 maunds/acre", "gross_margin": "Rs. 60,000/acre"},
            {"crop": "Cold-Hardy Vegetables (Peas, Cabbage)", "variety": "Meteor / Golden Acre", "sowing": "Sep 15 - Oct 20", "water_need": "Spring run", "yield": "180 bags/acre", "gross_margin": "Rs. 190,000/acre"}
        ],
        "cash_crops": ["Apple Orchards (Red Delicious, Gala)", "Walnut Groves", "Persimmon", "Plum"],
        "soil_action": "Construct stone terrace bunds to prevent steep slope erosion during monsoon downpours."
    },

    "islamabad": {
        "zone": "Margalla Foothills & Sub-Plateau Plain",
        "soil_type": "Medium Textured Loam with Limestone Matrix (pH 7.6)",
        "irrigation": "Rainfed + Rainwater Harvesting Dams / Tubewell",
        "kharif_crops": [
            {"crop": "Rainfed Maize", "variety": "Islamabad Gold / Sweet Corn", "sowing": "Jul 01 - Jul 25", "water_need": "350 mm", "yield": "40 - 55 maunds/acre", "gross_margin": "Rs. 100,000/acre"},
            {"crop": "Vegetable Tunnels", "variety": "Cucumber / Capsicum", "sowing": "Year-round", "water_need": "Drip Controlled", "yield": "High tunnel harvest", "gross_margin": "Rs. 400,000/acre"}
        ],
        "rabi_crops": [
            {"crop": "Rainfed Wheat", "variety": "Chakwal-50 / Akbar-2019", "sowing": "Nov 01 - Nov 20", "water_need": "300 mm", "yield": "35 - 45 maunds/acre", "gross_margin": "Rs. 110,000/acre"},
            {"crop": "Mustard / Sarson", "variety": "Canola", "sowing": "Oct 15 - Nov 10", "water_need": "220 mm", "yield": "20 maunds/acre", "gross_margin": "Rs. 85,000/acre"}
        ],
        "cash_crops": ["Hydroponic Greenhouses", "Olive Parcels", "Kitchen Garden Hubs"],
        "soil_action": "Contour farming along foothills to capture runoff and minimize soil displacement."
    }
}


def get_city_crop_profile(city_name: str) -> dict:
    """Returns the extensive crop agronomic profile for any Pakistan city."""
    key = city_name.lower().strip() if city_name else "chakwal"
    if key in REGIONAL_CROPS_DATA:
        return REGIONAL_CROPS_DATA[key]
    
    # Defaults based on Barani vs Irrigated
    if any(b in key for b in ["chakwal", "attock", "jhelum", "mianwali", "bhakkar", "kharian"]):
        profile = REGIONAL_CROPS_DATA["chakwal"].copy()
        profile["zone"] = f"{city_name.capitalize()} Rainfed Barani Agricultural Belt"
        return profile
    else:
        profile = REGIONAL_CROPS_DATA["lahore"].copy()
        profile["zone"] = f"{city_name.capitalize()} Irrigated Agricultural Basin"
        return profile
