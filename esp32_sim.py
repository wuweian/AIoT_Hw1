# -*- coding: utf-8 -*-
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
"""
ESP32 Simulator
  Mimics a WiFi-connected ESP32 running a DHT11 sensor.
  POSTs a JSON payload to Flask /sensor every 5 seconds.
  No network delay / packet loss simulation (clean demo mode).
"""
import requests
import random
import time
from datetime import datetime

# ── Config ─────────────────────────────────────────────────────────────────────
FLASK_URL   = "http://127.0.0.1:5000/sensor"
INTERVAL_S  = 5          # seconds between readings

# Simulated ESP32 WiFi metadata
DEVICE_ID   = "ESP32-SIM-001"
MAC_ADDRESS = "A4:CF:12:6E:3B:F0"
IP_ADDRESS  = "192.168.1.42"
SSID        = "IoT_Lab_WiFi"
BASE_RSSI   = -65        # dBm baseline

# DHT11 realistic ranges (integer-only like real hardware)
TEMP_MIN, TEMP_MAX = 20, 35   # °C
HUMI_MIN, HUMI_MAX = 40, 80   # %RH

# ─────────────────────────────────────────────────────────────────────────────
def build_payload() -> dict:
    return {
        "sensor":      "DHT11",
        "device_id":   DEVICE_ID,
        "mac_address": MAC_ADDRESS,
        "ip_address":  IP_ADDRESS,
        "ssid":        SSID,
        "rssi":        BASE_RSSI + random.randint(-5, 5),
        "temperature": random.randint(TEMP_MIN, TEMP_MAX),
        "humidity":    random.randint(HUMI_MIN, HUMI_MAX),
        "timestamp":   datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

def send_reading(seq: int):
    payload = build_payload()
    try:
        resp = requests.post(FLASK_URL, json=payload, timeout=5)
        resp.raise_for_status()
        body = resp.json()
        print(
            f"[ESP32] #{seq:>4}  {payload['timestamp']}  "
            f"Temp={payload['temperature']}C  "
            f"Humid={payload['humidity']}%RH  "
            f"RSSI={payload['rssi']}dBm  "
            f"-> DB id={body.get('id')} OK"
        )
    except requests.exceptions.ConnectionError:
        print(f"[ESP32] #{seq:>4}  ERR Connection refused -- is flask_api.py running?")
    except Exception as exc:
        print(f"[ESP32] #{seq:>4}  ERR {exc}")

def main():
    print("=" * 65)
    print(f"  ESP32 Simulator  |  Device : {DEVICE_ID}")
    print(f"  SSID : {SSID}   |  MAC : {MAC_ADDRESS}")
    print(f"  Posting to : {FLASK_URL}")
    print(f"  Interval   : {INTERVAL_S}s")
    print("=" * 65)

    seq = 1
    while True:
        send_reading(seq)
        seq += 1
        time.sleep(INTERVAL_S)

if __name__ == "__main__":
    main()
