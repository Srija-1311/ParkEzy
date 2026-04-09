"""
Preprocess PKLot UFPR04 dataset into SQLite analytics database.
Parses all XML annotation files and stores occupancy logs with weather info.

Weather mapping is based on the PKLot dataset documentation for UFPR04.
Run once: python tools/preprocess_pklot.py
"""

import os
import sqlite3
import xml.etree.ElementTree as ET
from datetime import datetime

XML_DIR = "data/UFPR04/xml"
DB_PATH = "data/analytics.db"

# PKLot UFPR04 weather mapping by date (from dataset documentation)
# Sunny=clear days, Cloudy=overcast, Rainy=rain/wet conditions
WEATHER_MAP = {
    "2012-12-07": "Cloudy",
    "2012-12-08": "Sunny",
    "2012-12-11": "Sunny",
    "2012-12-12": "Sunny",
    "2012-12-13": "Cloudy",
    "2012-12-14": "Rainy",
    "2012-12-15": "Rainy",
    "2012-12-16": "Cloudy",
    "2012-12-17": "Sunny",
    "2012-12-18": "Sunny",
    "2012-12-19": "Cloudy",
    "2012-12-20": "Rainy",
    "2012-12-21": "Sunny",
    "2012-12-22": "Sunny",
    "2012-12-23": "Cloudy",
    "2012-12-24": "Sunny",
    "2012-12-25": "Sunny",
    "2012-12-26": "Rainy",
    "2012-12-27": "Cloudy",
    "2012-12-28": "Sunny",
    "2012-12-29": "Sunny",
    "2013-01-15": "Sunny",
    "2013-01-16": "Cloudy",
    "2013-01-17": "Rainy",
    "2013-01-18": "Rainy",
    "2013-01-19": "Sunny",
    "2013-01-20": "Sunny",
    "2013-01-21": "Cloudy",
    "2013-01-22": "Sunny",
    "2013-01-29": "Rainy",
}

# --- Setup DB ---
os.makedirs("data", exist_ok=True)
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

c.execute("DROP TABLE IF EXISTS occupancy_logs")
c.execute("""
    CREATE TABLE occupancy_logs (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp       TEXT,
        date            TEXT,
        hour            INTEGER,
        weather         TEXT,
        occupied        INTEGER,
        vacant          INTEGER,
        total           INTEGER,
        occupancy_rate  REAL
    )
""")

inserted = 0
skipped = 0

for filename in sorted(os.listdir(XML_DIR)):
    if not filename.endswith(".xml"):
        continue

    xml_path = os.path.join(XML_DIR, filename)

    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()

        occupied = 0
        vacant = 0

        for space in root.findall(".//space"):
            status = None

            if "occupied" in space.attrib:
                status = int(space.attrib["occupied"])
            elif "free" in space.attrib:
                status = 0 if int(space.attrib["free"]) == 1 else 1
            else:
                occ_tag = space.find("occupied")
                if occ_tag is not None and occ_tag.text is not None:
                    status = int(occ_tag.text)

            if status is None:
                continue
            if status == 1:
                occupied += 1
            else:
                vacant += 1

        total = occupied + vacant
        rate = round(occupied / total, 4) if total else 0

        # Parse timestamp from filename: 2013-01-22_11_10_06.xml
        base = filename.replace(".xml", "")
        dt = datetime.strptime(base, "%Y-%m-%d_%H_%M_%S")
        date_str = dt.strftime("%Y-%m-%d")
        weather = WEATHER_MAP.get(date_str, "Unknown")

        c.execute("""
            INSERT INTO occupancy_logs
                (timestamp, date, hour, weather, occupied, vacant, total, occupancy_rate)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            dt.strftime("%Y-%m-%d %H:%M:%S"),
            date_str,
            dt.hour,
            weather,
            occupied,
            vacant,
            total,
            rate
        ))
        inserted += 1

    except Exception as e:
        print(f"  Skipped {filename}: {e}")
        skipped += 1

conn.commit()
conn.close()

print(f"Done. Inserted: {inserted} records, Skipped: {skipped}")
