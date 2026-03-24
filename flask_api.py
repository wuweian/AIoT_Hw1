"""
Flask AIoT API
  POST /sensor  → accept ESP32 DHT11 JSON payload, store in SQLite
  GET  /health  → liveness check
  GET  /data    → last N rows (JSON)
"""
from flask import Flask, request, jsonify
import sqlite3
from datetime import datetime

app = Flask(__name__)
DB = "aiotdb.db"

# ── DB helpers ────────────────────────────────────────────────────────────────
def get_conn():
    conn = sqlite3.connect(DB, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    c = conn.cursor()
    # Create table with full ESP32 metadata columns
    c.execute("""
        CREATE TABLE IF NOT EXISTS sensors (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            sensor      TEXT    NOT NULL DEFAULT 'DHT11',
            device_id   TEXT,
            mac_address TEXT,
            ip_address  TEXT,
            ssid        TEXT,
            rssi        INTEGER,
            temperature REAL    NOT NULL,
            humidity    REAL    NOT NULL,
            timestamp   TEXT    NOT NULL
        )
    """)
    # Gracefully add new columns to any existing DB
    extra_cols = [
        ("device_id",   "TEXT"),
        ("mac_address", "TEXT"),
        ("ip_address",  "TEXT"),
        ("ssid",        "TEXT"),
        ("rssi",        "INTEGER"),
    ]
    for col, dtype in extra_cols:
        try:
            c.execute(f"ALTER TABLE sensors ADD COLUMN {col} {dtype}")
        except Exception:
            pass  # column already exists
    conn.commit()
    conn.close()
    print(f"[FLASK] DB '{DB}' ready — table 'sensors' initialised.")

# ── Routes ────────────────────────────────────────────────────────────────────
@app.route("/health", methods=["GET"])
def health():
    conn = get_conn()
    count = conn.execute("SELECT COUNT(*) FROM sensors").fetchone()[0]
    conn.close()
    return jsonify({
        "status":  "ok",
        "db":      DB,
        "records": count,
        "time":    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    })

@app.route("/sensor", methods=["POST"])
def sensor():
    data = request.get_json(force=True, silent=True)
    if not data:
        return jsonify({"error": "Invalid or missing JSON body"}), 400

    temp = data.get("temperature")
    humi = data.get("humidity")
    if temp is None or humi is None:
        return jsonify({"error": "temperature and humidity are required"}), 400

    row = {
        "sensor":      data.get("sensor",      "DHT11"),
        "device_id":   data.get("device_id",   "ESP32-UNKNOWN"),
        "mac_address": data.get("mac_address", ""),
        "ip_address":  data.get("ip_address",  ""),
        "ssid":        data.get("ssid",        ""),
        "rssi":        data.get("rssi",        None),
        "temperature": float(temp),
        "humidity":    float(humi),
        "timestamp":   data.get("timestamp",   datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
    }

    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        INSERT INTO sensors
            (sensor, device_id, mac_address, ip_address, ssid, rssi, temperature, humidity, timestamp)
        VALUES
            (:sensor, :device_id, :mac_address, :ip_address, :ssid, :rssi, :temperature, :humidity, :timestamp)
    """, row)
    conn.commit()
    row_id = c.lastrowid
    conn.close()

    print(
        f"[FLASK]  #{row_id:>4}  {row['timestamp']}  "
        f"{row['device_id']}  {row['temperature']}°C  {row['humidity']}%RH  "
        f"RSSI={row['rssi']}dBm"
    )
    return jsonify({"status": "ok", "id": row_id, "timestamp": row["timestamp"]}), 201

@app.route("/data", methods=["GET"])
def data():
    limit = int(request.args.get("limit", 50))
    conn  = get_conn()
    rows  = conn.execute(
        "SELECT * FROM sensors ORDER BY id DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    init_db()
    print("[FLASK] Server starting on http://0.0.0.0:5000")
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)
