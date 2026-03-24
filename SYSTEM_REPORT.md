# AIoT Homework 1 — System Report

**Date of Generation**: 2026-03-24  
**Project Repository**: [https://github.com/wuweian/AIoT_Hw1](https://github.com/wuweian/AIoT_Hw1.git)  
**Author**: Antigravity (Google DeepMind) on behalf of User

This document serves as the formal system report detailing the architecture, implementation steps, and capabilities of the completed AIoT Demo.

---

## 1. System Overview
The system simulates a complete, end-to-end AIoT (Artificial Intelligence of Things) pipeline. It mirrors the process of obtaining hardware sensor readings from an edge device, securely transmitting those readings over a simulated network to a centralized server, storing that data for persistence, and querying that data for real-time visualization.

### Key Features Implemented:
*   **Hardware Simulation (`esp32_sim.py`)**: A Python thread that accurately simulates an ESP32 microcontroller with a connected DHT11 sensor.
*   **Data Aggregation API (`flask_api.py`)**: A Flask-based RESTful backend that provides a `/sensor` endpoint to ingest the HTTP POST requests seamlessly.
*   **Persistent Storage (`aiotdb.db`)**: A SQLite3 database enforcing a rigid schema `sensors` for high-fidelity data logging.
*   **Real-time Dashboard (`streamlit_app.py`)**: A professional UI built with Streamlit and Plotly, polling the DB incrementally and displaying rolling averages, KPI metics, and raw telemetry data.

---

## 2. Technical Stack & Architectures

| Component | Technology | Purpose |
| :--- | :--- | :--- |
| **Edge Node** | Python `requests`, `random` | Generate randomized integer data mirroring real DHT11 hardware (Temp: 20-35°C, Humid: 40-80%RH). |
| **Backend API** | Flask | Provide HTTP lifecycle management; bind the endpoints `/health`, `/sensor`, and `/data`. |
| **Database Layer** | SQLite3 | Local `.db` file mapping telemetry dictionaries into relational rows (`id`, `timestamp`, `temperature`, `humidity`, `device_id`, etc.). |
| **Frontend UI** | Streamlit, Pandas, Plotly | Translate SQL dataframes into a live, rich user-facing web format via port `8502`. |
| **Virtual Env.** | Python `venv` | Ensure strict dependency constraints (`requirements.txt`) so the stack remains reproducible. |

---

## 3. Data Flow & Security
1. **ESP32 Simulator (`esp32_sim.py`)** creates JSON containing simulated environmental conditions + WiFi Metadata (MAC Address, SSID, IP, RSSI).
2. The data is packaged in an HTTP POST request and sent via `UTF-8` payload over localhost to `http://0.0.0.0:5000/sensor`.
3. The **Flask Process** receives the JSON request, verifies keys, and securely injects it into `aiotdb.db` using parameterised SQLite queries to prevent SQL injection.
4. The **Streamlit Process** executes a strict `SELECT * FROM sensors ORDER BY id DESC LIMIT N` query every 3/5 seconds and re-renders the DOM, offering live updates to anyone traversing `http://localhost:8502`.

---

## 4. API Endpoints
*   `GET /health`: Used for system load balancers and deployment verification. Returns `{ "status": "ok", "records": INT, "db": "aiotdb.db" }`.
*   `POST /sensor`: Protected interface. Validates incoming payload format and enforces presence of `temperature` and `humidity` values.
*   `GET /data?limit=50`: Utility endpoint configured to retrieve historical JSON chunks seamlessly.

---

## 5. Implementation Summary
The development of this AIoT system successfully hit all predefined homework constraints:
*   ✅ **SQLite Table Created**: Schema contains extra tracing variables (IP, MAC, RSSI) in case of physical router deployments.
*   ✅ **Simulation Accuracy**: DHT11 produces strictly integer limits based closely on factory tolerance ranges.
*   ✅ **Python Virtualization**: The isolated python environment removes OS-level dependency clashes.
*   ✅ **Data Visualisation**: The metrics dashboard accurately represents telemetry via scatter+line charts alongside numeric aggregators (averages and differentials).
*   ✅ **Version Control**: Committed to GitHub `main` branch correctly containing `.gitignore` and `README.md`.
