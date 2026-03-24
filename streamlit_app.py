"""
Streamlit AIoT Dashboard  ·  reads aiotdb.db → displays ESP32 DHT11 data
"""
import sqlite3
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime

# ── Page setup ─────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AIoT Dashboard – ESP32 / DHT11",
    page_icon="📡",
    layout="wide",
)

# ── Styling ────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');

html, body, [data-testid="stAppViewContainer"] {
    font-family: 'Inter', sans-serif;
    background: linear-gradient(135deg, #0a0a1a 0%, #12122a 50%, #0d1b2a 100%);
    color: #e2e8f0;
}
[data-testid="stHeader"]  { background: transparent; }
[data-testid="stSidebar"] {
    background: rgba(255,255,255,0.03);
    border-right: 1px solid rgba(255,255,255,0.08);
}

/* Metric cards */
[data-testid="metric-container"] {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.10);
    border-radius: 14px;
    padding: 18px 22px;
}
[data-testid="stMetricLabel"] { color: #94a3b8 !important; font-size:0.82rem; letter-spacing:.04em; text-transform:uppercase; }
[data-testid="stMetricValue"] { color: #f8fafc  !important; font-size:2rem; font-weight:800; }

/* Title gradient */
.hero-title {
    font-size: 2rem; font-weight: 800;
    background: linear-gradient(90deg, #38bdf8 0%, #818cf8 50%, #f472b6 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.hero-sub { color:#64748b; font-size:.9rem; margin-bottom:1.2rem; }

/* Status pills */
.pill { display:inline-block; padding:2px 10px; border-radius:999px; font-size:.75rem; font-weight:700; }
.live  { background:#22c55e18; color:#22c55e; border:1px solid #22c55e40; }
.empty { background:#ef444418; color:#ef4444; border:1px solid #ef444440; }

/* Device badge */
.badge {
    display:inline-block; font-size:.75rem; padding:3px 9px;
    background:rgba(129,140,248,.15); color:#818cf8;
    border:1px solid rgba(129,140,248,.3); border-radius:6px; margin-right:6px;
}
</style>
""", unsafe_allow_html=True)

DB = "aiotdb.db"
REFRESH_S = 3

# ── Data ──────────────────────────────────────────────────────────────────────
@st.cache_data(ttl=REFRESH_S)
def load(limit: int = 100) -> pd.DataFrame:
    try:
        conn = sqlite3.connect(DB)
        df = pd.read_sql_query(
            "SELECT * FROM sensors ORDER BY id DESC LIMIT ?",
            conn, params=(limit,)
        )
        conn.close()
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        return df.sort_values("id").reset_index(drop=True)
    except Exception:
        return pd.DataFrame()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 📡 AIoT Settings")
    limit       = st.slider("Records", 20, 500, 100, 10)
    auto        = st.toggle("Auto-refresh", value=True)
    chart_type  = st.selectbox("Chart style", ["Lines + Markers", "Lines", "Markers"])
    st.divider()
    st.markdown("**Stack**")
    st.markdown("- ESP32 simulator → HTTP POST")
    st.markdown("- Flask `/sensor` endpoint")
    st.markdown("- SQLite3 `aiotdb.db`")
    st.markdown("- Streamlit dashboard")
    st.divider()
    st.markdown("**DB:** `aiotdb.db` · **Table:** `sensors`")
    st.markdown("**Sensor:** DHT11 · **Interval:** 5 s")

# ── Load data ─────────────────────────────────────────────────────────────────
df = load(limit)

# ── Header ────────────────────────────────────────────────────────────────────
pill = '<span class="pill live">● LIVE</span>' if not df.empty else '<span class="pill empty">● NO DATA — start esp32_sim.py & flask_api.py</span>'
st.markdown(f'<p class="hero-title">📡 AIoT Live Dashboard &nbsp; {pill}</p>', unsafe_allow_html=True)

if not df.empty and "device_id" in df.columns:
    devices = df["device_id"].dropna().unique()
    badges  = " ".join(f'<span class="badge">{d}</span>' for d in devices)
    st.markdown(f'<p class="hero-sub">Devices: {badges}</p>', unsafe_allow_html=True)
else:
    st.markdown('<p class="hero-sub">Awaiting ESP32 data…</p>', unsafe_allow_html=True)

# ── KPI cards ─────────────────────────────────────────────────────────────────
if not df.empty:
    latest = df.iloc[-1]
    prev   = df.iloc[-2] if len(df) > 1 else latest

    k1, k2, k3, k4, k5, k6 = st.columns(6)
    k1.metric("🌡 Temperature",   f"{latest['temperature']:.0f} °C",
              f"{latest['temperature']-prev['temperature']:+.0f} °C")
    k2.metric("💧 Humidity",      f"{latest['humidity']:.0f} %",
              f"{latest['humidity']-prev['humidity']:+.0f} %")
    k3.metric("📊 Avg Temp",      f"{df['temperature'].mean():.1f} °C")
    k4.metric("📊 Avg Humidity",  f"{df['humidity'].mean():.1f} %")
    k5.metric("📦 Records",       len(df))
    if "rssi" in df.columns:
        rssi_val = df["rssi"].dropna()
        k6.metric("📶 Avg RSSI", f"{rssi_val.mean():.0f} dBm" if not rssi_val.empty else "—")
    else:
        k6.metric("📶 RSSI", "—")
else:
    st.warning("⚠️ No records yet. Run `flask_api.py` then `esp32_sim.py`.")
    st.stop()

st.divider()

# ── Charts ────────────────────────────────────────────────────────────────────
mode_map = {"Lines + Markers": "lines+markers", "Lines": "lines", "Markers": "markers"}
mode = mode_map[chart_type]

fig = make_subplots(
    rows=2, cols=1,
    shared_xaxes=True,
    vertical_spacing=0.12,
    subplot_titles=("🌡  Temperature (°C)", "💧  Humidity (%RH)"),
)

# Temperature
fig.add_trace(go.Scatter(
    x=df["timestamp"], y=df["temperature"],
    mode=mode, name="Temperature",
    line=dict(color="#fbbf24", width=2.5),
    marker=dict(size=5, color="#f59e0b"),
    fill="tozeroy", fillcolor="rgba(251,191,36,0.08)",
    hovertemplate="<b>%{x|%H:%M:%S}</b><br>Temp: %{y}°C<extra></extra>",
), row=1, col=1)

# Humidity
fig.add_trace(go.Scatter(
    x=df["timestamp"], y=df["humidity"],
    mode=mode, name="Humidity",
    line=dict(color="#38bdf8", width=2.5),
    marker=dict(size=5, color="#0ea5e9"),
    fill="tozeroy", fillcolor="rgba(56,189,248,0.08)",
    hovertemplate="<b>%{x|%H:%M:%S}</b><br>Humid: %{y}%<extra></extra>",
), row=2, col=1)

# Normal-range bands
fig.add_hrect(y0=20, y1=35, row=1, col=1,
              fillcolor="rgba(34,197,94,0.06)", line_width=0,
              annotation_text="Normal 20–35°C", annotation_position="top left",
              annotation_font=dict(color="#22c55e", size=11))
fig.add_hrect(y0=40, y1=80, row=2, col=1,
              fillcolor="rgba(34,197,94,0.06)", line_width=0,
              annotation_text="Normal 40–80%", annotation_position="top left",
              annotation_font=dict(color="#22c55e", size=11))

fig.update_layout(
    height=520,
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(255,255,255,0.02)",
    font=dict(color="#94a3b8", family="Inter"),
    showlegend=False,
    margin=dict(l=10, r=10, t=45, b=10),
)
for axis in ["xaxis", "xaxis2", "yaxis", "yaxis2"]:
    fig.update_layout(**{
        axis: dict(
            gridcolor="rgba(255,255,255,0.06)",
            color="#64748b",
            **( {"tickformat": "%H:%M:%S"} if "x" in axis else {} ),
            **( {"range": [0, 55]}  if axis == "yaxis"  else {} ),
            **( {"range": [0, 100]} if axis == "yaxis2" else {} ),
        )
    })

st.plotly_chart(fig, use_container_width=True)

# ── Raw data table ────────────────────────────────────────────────────────────
with st.expander("📋 Raw sensor data (latest first)", expanded=False):
    show_cols = [c for c in
                 ["id","timestamp","sensor","device_id","mac_address","ssid","rssi","temperature","humidity"]
                 if c in df.columns]
    display = df[show_cols].sort_values("id", ascending=False).reset_index(drop=True)
    col_names = {
        "id": "ID", "timestamp": "Timestamp", "sensor": "Sensor",
        "device_id": "Device", "mac_address": "MAC", "ssid": "SSID",
        "rssi": "RSSI (dBm)", "temperature": "Temp (°C)", "humidity": "Humid (%)",
    }
    display.rename(columns=col_names, inplace=True)
    st.dataframe(display, use_container_width=True, hide_index=True)

# ── Footer ────────────────────────────────────────────────────────────────────
st.caption(f"🕐 Refreshed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  ·  DB: {DB}  ·  Refresh every {REFRESH_S}s")

# ── Auto-refresh ──────────────────────────────────────────────────────────────
if auto:
    import time
    time.sleep(REFRESH_S)
    st.rerun()
