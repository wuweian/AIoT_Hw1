import sqlite3
import random
import time
from datetime import datetime

# ── Database setup ────────────────────────────────────────────────────────────
DB_NAME = "aiotdb.db"

def init_db():
    """Create the sensors table if it doesn't exist."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sensors (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            sensor      TEXT    NOT NULL DEFAULT 'DHT11',
            temperature REAL    NOT NULL,
            humidity    REAL    NOT NULL,
            timestamp   TEXT    NOT NULL
        )
    """)
    conn.commit()
    conn.close()
    print(f"[DB] Connected to '{DB_NAME}', table 'sensors' ready.")

# ── DHT11 simulation ──────────────────────────────────────────────────────────
def read_dht11():
    """
    Simulate a DHT11 reading.
      - Temperature : 0–50 °C  (realistic indoor: 20–35)
      - Humidity    : 20–90 %RH (realistic indoor: 40–80)
    DHT11 reports in whole integers only.
    """
    temperature = random.randint(20, 35)   # °C
    humidity    = random.randint(40, 80)   # %RH
    return temperature, humidity

# ── Insert reading ────────────────────────────────────────────────────────────
def insert_reading(temperature, humidity):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO sensors (sensor, temperature, humidity, timestamp)
        VALUES (?, ?, ?, ?)
    """, ("DHT11", temperature, humidity, timestamp))
    conn.commit()
    row_id = cursor.lastrowid
    conn.close()
    return row_id, timestamp

# ── Main loop ─────────────────────────────────────────────────────────────────
def main():
    init_db()
    print("[SIM] DHT11 simulator started. Press Ctrl+C to stop.\n")
    print(f"{'ID':<6} {'Timestamp':<22} {'Sensor':<8} {'Temp (°C)':<12} {'Humidity (%)'}")
    print("-" * 64)

    try:
        while True:
            temp, humi = read_dht11()
            row_id, ts = insert_reading(temp, humi)
            print(f"{row_id:<6} {ts:<22} {'DHT11':<8} {temp:<12} {humi}")
            time.sleep(2)

    except KeyboardInterrupt:
        print("\n[SIM] Stopped by user.")

if __name__ == "__main__":
    main()
