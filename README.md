# AIoT Homework 1 — ESP32 DHT11 Local Demo

A local Python AIoT demo stack simulating a **WiFi-connected ESP32** with a **DHT11** temperature & humidity sensor. Data flows from the simulator → Flask REST API → SQLite3 → Streamlit live dashboard.

---

## Architecture

```
esp32_sim.py  ──HTTP POST /sensor──►  flask_api.py  ──INSERT──►  aiotdb.db (SQLite3)
                                                                        │
                                                               streamlit_app.py
                                                               (reads & visualises)
```

## Files

| File | Description |
|---|---|
| `flask_api.py` | Flask REST API — `POST /sensor`, `GET /health`, `GET /data` |
| `esp32_sim.py` | ESP32 WiFi + DHT11 simulator — HTTP POST every 5 seconds |
| `streamlit_app.py` | Live AIoT dashboard — KPIs, temperature & humidity charts |
| `dashboard.py` | Standalone DHT11 dashboard (reads direct from DB) |
| `dht11_simulator.py` | Standalone DHT11 data generator → SQLite3 (every 2 s) |
| `requirements.txt` | Python dependencies |
| `log.md` | Session log |

---

## Setup

```bash
# 1. Create virtual environment
python -m venv venv

# 2. Activate (Windows CMD)
venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
```

---

## Run (3 terminals)

```bash
# Terminal 1 — Flask API (port 5000)
venv\Scripts\python.exe flask_api.py

# Terminal 2 — ESP32 Simulator (posts every 5s)
venv\Scripts\python.exe esp32_sim.py

# Terminal 3 — Streamlit Dashboard (port 8502)
venv\Scripts\python.exe -m streamlit run streamlit_app.py --server.port 8502
```

## Endpoints

| Method | URL | Description |
|---|---|---|
| `GET` | `http://localhost:5000/health` | Health check + record count |
| `POST` | `http://localhost:5000/sensor` | Ingest sensor reading (JSON) |
| `GET` | `http://localhost:5000/data?limit=50` | Last N records (JSON) |
| `GET` | `http://localhost:8502` | Streamlit live dashboard |

## Sensor Payload (ESP32 → Flask)

```json
{
  "sensor":      "DHT11",
  "device_id":   "ESP32-SIM-001",
  "mac_address": "A4:CF:12:6E:3B:F0",
  "ip_address":  "192.168.1.42",
  "ssid":        "IoT_Lab_WiFi",
  "rssi":        -65,
  "temperature": 27,
  "humidity":    65,
  "timestamp":   "2026-03-24 11:30:00"
}
```

## Database Schema

```sql
CREATE TABLE sensors (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    sensor      TEXT,
    device_id   TEXT,
    mac_address TEXT,
    ip_address  TEXT,
    ssid        TEXT,
    rssi        INTEGER,
    temperature REAL NOT NULL,
    humidity    REAL NOT NULL,
    timestamp   TEXT NOT NULL
);
```

---

## Requirements

- Python 3.10+
- `flask`, `requests`, `streamlit`, `plotly`, `pandas`
