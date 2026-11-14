"""
NASA / FAO Global Crop Catalog Service (549 Species & Cultivars)
================================================================
Queries the SQLite catalog of 549 agricultural crops with NASA Earth Observation
monitoring variables (SMAP, GPM, MODIS, Landsat), FAO EcoCrop/GAEZ parameters,
scientific nomenclature, and agronomic management profiles.
"""

import sqlite3
import os
from typing import List, Dict, Any, Optional

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "nasa_crops_catalog.db")
SQL_FILE = os.path.join(BASE_DIR, "crop_database.sql")

def get_connection():
    """Returns a connection to the SQLite crops database, initializing it if absent."""
    if not os.path.exists(DB_FILE):
        _initialize_db_if_needed()
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def _initialize_db_if_needed():
    """Auto-populates SQLite database from SQL file if the database does not exist."""
    if os.path.exists(SQL_FILE):
        conn = sqlite3.connect(DB_FILE)
        with open(SQL_FILE, "r", encoding="utf-8") as f:
            conn.executescript(f.read())
        cursor = conn.cursor()
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_crop_name ON crops(crop_name);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_crop_group ON crops(crop_group);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_scientific_name ON crops(scientific_name);")
        conn.commit()
        conn.close()

def get_crop_stats() -> Dict[str, Any]:
    """Returns statistical metrics regarding the 549 crop catalog."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM crops;")
        total = cursor.fetchone()[0]

        cursor.execute("""
            SELECT crop_group, COUNT(*) as cnt 
            FROM crops 
            GROUP BY crop_group 
            ORDER BY cnt DESC;
        """)
        groups = [{"group": row["crop_group"], "count": row["cnt"]} for row in cursor.fetchall()]

        cursor.execute("SELECT COUNT(DISTINCT scientific_name) FROM crops WHERE scientific_name IS NOT NULL;")
        distinct_species = cursor.fetchone()[0]

        return {
            "total_crops": total,
            "groups_count": len(groups),
            "distinct_species": distinct_species,
            "groups": groups,
            "nasa_monitored_sensors": ["SMAP (Soil Moisture)", "GPM (Precipitation)", "MODIS (NDVI/EVI)", "Landsat-8/9 (Land Surface Temp)"]
        }

def get_crop_groups() -> List[str]:
    """Returns list of distinct crop group classifications."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT crop_group FROM crops WHERE crop_group IS NOT NULL ORDER BY crop_group ASC;")
        return [row["crop_group"] for row in cursor.fetchall()]

def search_crops(
    query: Optional[str] = None, 
    group: Optional[str] = None, 
    limit: int = 50, 
    offset: int = 0
) -> Dict[str, Any]:
    """
    Searches the 549 crop catalog by keyword, group, or both.
    Keyword searches match against crop_name, scientific_name, common_uses, or crop_id.
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        conditions = []
        params = []

        if query and query.strip():
            q_clean = f"%{query.strip().lower()}%"
            conditions.append("""(
                LOWER(crop_name) LIKE ? OR 
                LOWER(scientific_name) LIKE ? OR 
                LOWER(common_uses) LIKE ? OR 
                LOWER(crop_id) LIKE ?
            )""")
            params.extend([q_clean, q_clean, q_clean, q_clean])

        if group and group.strip() and group.strip().lower() != "all":
            conditions.append("LOWER(crop_group) = ?")
            params.append(group.strip().lower())

        where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

        # Total matching count
        count_sql = f"SELECT COUNT(*) FROM crops {where_clause};"
        cursor.execute(count_sql, params)
        total_matched = cursor.fetchone()[0]

        # Paginated results
        fetch_sql = f"""
            SELECT 
                crop_id, crop_name, scientific_name, crop_group, record_type,
                common_uses, growth_cycle_days, optimal_temp_min_c, optimal_temp_max_c,
                annual_rainfall_min_mm, annual_rainfall_max_mm, soil_ph_min, soil_ph_max,
                water_requirement, planting_season, harvest_season,
                nasa_monitoring_variables, nasa_data_sources, agronomy_reference,
                agronomy_reference_url, data_quality_note
            FROM crops 
            {where_clause}
            ORDER BY crop_id ASC
            LIMIT ? OFFSET ?;
        """
        cursor.execute(fetch_sql, params + [limit, offset])
        rows = [dict(row) for row in cursor.fetchall()]

        return {
            "query": query,
            "group": group,
            "total_matches": total_matched,
            "limit": limit,
            "offset": offset,
            "crops": rows
        }

def get_crop_by_id(crop_id: str) -> Optional[Dict[str, Any]]:
    """Fetches complete profile for a single crop by its catalog ID (e.g. CR0001)."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM crops WHERE LOWER(crop_id) = ?;", (crop_id.strip().lower(),))
        row = cursor.fetchone()
        return dict(row) if row else None

def link_regional_to_catalog(regional_crop_name: str) -> Optional[Dict[str, Any]]:
    """
    Intelligently links a Pakistan regional crop name (e.g. 'Rainfed Wheat', 'Super Basmati Rice')
    to the global FAO/NASA 549 catalog entry.
    """
    clean = regional_crop_name.lower()
    # Key mapping rules for Pakistan agronomy
    aliases = {
        "wheat": "Wheat",
        "rice": "Rice",
        "basmati": "Rice",
        "maize": "Maize",
        "corn": "Maize",
        "cotton": "Cotton",
        "mustard": "Mustard",
        "sarson": "Mustard",
        "canola": "Rapeseed",
        "raya": "Mustard",
        "gram": "Chickpea",
        "chickpea": "Chickpea",
        "groundnut": "Peanut",
        "peanut": "Peanut",
        "potato": "Potato",
        "mungbean": "Mung bean",
        "mung": "Mung bean",
        "sesame": "Sesame",
        "til": "Sesame",
        "sorghum": "Sorghum",
        "jowar": "Sorghum",
        "millet": "Pearl millet",
        "bajra": "Pearl millet",
        "berseem": "Berseem clover",
        "sunflower": "Sunflower",
        "olive": "Olive",
        "tomato": "Tomato",
        "citrus": "Sweet orange",
        "kinnow": "Mandarin orange",
        "mango": "Mango",
        "guava": "Common guava",
        "apple": "Apple",
        "barley": "Barley"
    }

    target = None
    for k, v in aliases.items():
        if k in clean:
            target = v
            break

    if target:
        results = search_crops(query=target, limit=1)
        if results["crops"]:
            return results["crops"][0]

    # Fallback direct search
    results = search_crops(query=regional_crop_name.split()[0], limit=1)
    return results["crops"][0] if results["crops"] else None


if __name__ == "__main__":
    print("Testing crop_catalog_service...")
    stats = get_crop_stats()
    print("Stats:", stats["total_crops"], "crops across", stats["groups_count"], "groups")
    
    wheat_search = search_crops(query="wheat", limit=3)
    print(f"Found {wheat_search['total_matches']} wheat matches:")
    for c in wheat_search["crops"]:
        print(f" - [{c['crop_id']}] {c['crop_name']} ({c['scientific_name']}) - {c['crop_group']}")

    linked = link_regional_to_catalog("Rainfed Wheat")
    print(f"Linked 'Rainfed Wheat' -> [{linked.get('crop_id')}] {linked.get('crop_name')} ({linked.get('scientific_name')})")
