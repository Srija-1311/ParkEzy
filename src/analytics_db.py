import sqlite3
import os

DB_PATH = "data/analytics.db"


def init_db():
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS occupancy_logs (
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
    # Slot-level utilization table (populated by evaluate route)
    c.execute("""
        CREATE TABLE IF NOT EXISTS slot_utilization (
            slot_id         TEXT PRIMARY KEY,
            gt_occupied_pct REAL,
            accuracy        REAL,
            tp INTEGER, fp INTEGER, tn INTEGER, fn INTEGER
        )
    """)
    c.execute("""
    CREATE TABLE IF NOT EXISTS frame_data (
        frame INTEGER,
        available INTEGER
    )
""")
    conn.commit()
    conn.close()


def log_occupancy(occupied, vacant, weather="Unknown"):
    from datetime import datetime
    total = occupied + vacant
    rate  = round(occupied / total, 4) if total else 0
    now   = datetime.now()
    conn  = sqlite3.connect(DB_PATH)
    c     = conn.cursor()
    c.execute("""
        INSERT INTO occupancy_logs
            (timestamp, date, hour, weather, occupied, vacant, total, occupancy_rate)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        now.strftime("%Y-%m-%d %H:%M:%S"),
        now.strftime("%Y-%m-%d"),
        now.hour, weather,
        occupied, vacant, total, rate
    ))
    conn.commit()
    conn.close()


def save_slot_utilization(per_slot):
    conn = sqlite3.connect(DB_PATH)
    c    = conn.cursor()
    c.execute("DELETE FROM slot_utilization")
    c.executemany("""
        INSERT INTO slot_utilization
            (slot_id, gt_occupied_pct, accuracy, tp, fp, tn, fn)
        VALUES (:slot_id, :gt_occupied_pct, :accuracy, :tp, :fp, :tn, :fn)
    """, per_slot)
    conn.commit()
    conn.close()


def get_slot_utilization():
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute("""
        SELECT slot_id, gt_occupied_pct, accuracy, tp, fp, tn, fn
        FROM slot_utilization
        ORDER BY CAST(slot_id AS INTEGER)
    """).fetchall()
    conn.close()
    return [
        {"slot_id": r[0], "gt_occupied_pct": r[1], "accuracy": r[2],
         "tp": r[3], "fp": r[4], "tn": r[5], "fn": r[6]}
        for r in rows
    ]

def save_frame_data(frame_id, available):
    conn = sqlite3.connect(DB_PATH)   # ✅ FIX
    c = conn.cursor()

    c.execute(
        "INSERT INTO frame_data (frame, available) VALUES (?, ?)",
        (frame_id, available)
    )

    conn.commit()
    conn.close()
def clear_frame_data():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("DELETE FROM frame_data")
    conn.commit()
    conn.close()