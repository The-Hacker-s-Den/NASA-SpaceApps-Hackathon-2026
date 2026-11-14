"""
Import and initialize the 549 NASA/FAO Crops Catalog Database into SQLite.
"""
import sqlite3
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SQL_FILE = os.path.join(BASE_DIR, "crop_database.sql")
DB_FILE = os.path.join(BASE_DIR, "nasa_crops_catalog.db")

def init_db():
    print(f"Reading SQL file from: {SQL_FILE}")
    if not os.path.exists(SQL_FILE):
        print(f"Error: {SQL_FILE} not found!")
        sys.exit(1)

    with open(SQL_FILE, "r", encoding="utf-8") as f:
        sql_content = f.read()

    print(f"Connecting to SQLite: {DB_FILE}")
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Drop existing table if refreshing
    cursor.execute("DROP TABLE IF EXISTS crops;")
    conn.commit()

    # Execute SQL script
    cursor.executescript(sql_content)
    conn.commit()

    # Verify counts
    cursor.execute("SELECT COUNT(*) FROM crops;")
    total = cursor.fetchone()[0]
    print(f"SUCCESS: Ingested {total} crops into {DB_FILE}")

    # Create search indexes for ultra-fast autocomplete and query
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_crop_name ON crops(crop_name);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_crop_group ON crops(crop_group);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_scientific_name ON crops(scientific_name);")
    conn.commit()
    print("SUCCESS: Created performance indexes on crop_name, crop_group, and scientific_name.")

    # Breakdown by crop_group
    cursor.execute("SELECT crop_group, COUNT(*) FROM crops GROUP BY crop_group ORDER BY COUNT(*) DESC;")
    groups = cursor.fetchall()
    print(f"\nBreakdown across {len(groups)} distinct crop groups:")
    for group, count in groups:
        print(f"  - {group}: {count} crops")

    # Sample rows
    cursor.execute("SELECT crop_id, crop_name, scientific_name, crop_group FROM crops LIMIT 5;")
    samples = cursor.fetchall()
    print("\nSample crops:")
    for s in samples:
        print(f"  [{s[0]}] {s[1]} ({s[2]}) - Group: {s[3]}")

    conn.close()
    return total

if __name__ == "__main__":
    init_db()
