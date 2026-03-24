import sqlite3
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="DHT11 Live Dashboard",
    page_icon="🌡️",
    layout="wide",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  /* Dark gradient background */
  [data-testid="stAppViewContainer"] {
      background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
      color: #f0f0f0;
  }
  [data-testid="stHeader"] { background: transparent; }
  [data-testid="stSidebar"] { background: rgba(255,255,255,0.04); }

  /* Metric cards */
  [data-testid="metric-container"] {
      background: rgba(255,255,255,0.07);
      border: 1px solid rgba(255,255,255,0.12);
      border-radius: 16px;
      padding: 20px 28px;
      backdrop-filter: blur(10px);
  }
  [data-testid="stMetricLabel"]  { color: #a0aec0 !important; font-size: 0.85rem; }
  [data-testid="stMetricValue"]  { color: #ffffff !important; font-size: 2.4rem; font-weight: 700; }
  [data-testid="stMetricDelta"]  { font-size: 0.9rem; }

  /* Title */
  .dash-title {
      font-size: 2.2rem; font-weight: 800;
      background: linear-gradient(90deg, #f6d365, #fda085);
      -webkit-background-clip: text; -webkit-text-fill-color: transparent;
      margin-bottom: 0;
  }
  .dash-sub {
      color: #a0aec0; font-size: 0.95rem; margin-top: 4px; margin-bottom: 24px;
  }
  /* Status pill */
  .pill {
      display:inline-block; padding:3px 12px; border-radius:999px;
      font-size:0.78rem; font-weight:600; margin-left:10px;
  }
  .pill-live  { background:#22c55e22; color:#22c55e; border:1px solid #22c55e55; }
  .pill-empty { background:#ef444422; color:#ef4444; border:1px solid #ef444455; }
</style>
""", unsafe_allow_html=True)

DB_NAME = "aiotdb.db"
REFRESH_SEC = 2   # auto-refresh interval

# ── Data loader ───────────────────────────────────────────────────────────────
@st.cache_data(ttl=REFRESH_SEC)
def load_data(limit: int = 50) -> pd.DataFrame:
    try:
        conn = sqlite3.connect(DB_NAME)
        df = pd.read_sql_query(
            f"SELECT id, temperature, humidity, timestamp FROM sensors ORDER BY id DESC LIMIT {limit}",
            conn
        )
        conn.close()
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        return df.sort_values("id").reset_index(drop=True)
    except Exception:
        return pd.DataFrame(columns=["id", "temperature", "humidity", "timestamp"])

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    limit = st.slider("Records to display", 10, 200, 50, 10)
    auto_refresh = st.toggle("Auto-refresh", value=True)
    st.markdown("---")
    st.markdown("**Database:** `aiotdb.db`")
    st.markdown("**Table:** `sensors`")
    st.markdown("**Sensor:** DHT11")
    st.markdown("**Interval:** 2 s")

# ── Header ────────────────────────────────────────────────────────────────────
df = load_data(limit)

status_pill = (
    '<span class="pill pill-live">● LIVE</span>'
    if not df.empty else
    '<span class="pill pill-empty">● NO DATA</span>'
)
st.markdown(f'<p class="dash-title">🌡️ DHT11 Live Dashboard {status_pill}</p>', unsafe_allow_html=True)
st.markdown('<p class="dash-sub">Real-time temperature &amp; humidity from simulated DHT11 sensor</p>', unsafe_allow_html=True)

# ── KPI metrics ───────────────────────────────────────────────────────────────
if not df.empty:
    latest = df.iloc[-1]
    prev   = df.iloc[-2] if len(df) > 1 else latest

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("🌡️ Temperature",  f"{latest['temperature']:.0f} °C",
              delta=f"{latest['temperature'] - prev['temperature']:+.0f} °C")
    c2.metric("💧 Humidity",     f"{latest['humidity']:.0f} %",
              delta=f"{latest['humidity'] - prev['humidity']:+.0f} %")
    c3.metric("📈 Avg Temp",     f"{df['temperature'].mean():.1f} °C")
    c4.metric("📈 Avg Humidity", f"{df['humidity'].mean():.1f} %")
    c5.metric("📦 Total Records", len(df))
else:
    st.warning("⚠️ No data yet. Make sure `dht11_simulator.py` is running.")

st.markdown("---")

# ── Charts ────────────────────────────────────────────────────────────────────
if not df.empty:
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.10,
        subplot_titles=("Temperature (°C)", "Humidity (%RH)")
    )

    # — Temperature line
    fig.add_trace(go.Scatter(
        x=df["timestamp"], y=df["temperature"],
        mode="lines+markers",
        name="Temperature",
        line=dict(color="#f6d365", width=2.5),
        marker=dict(size=5, color="#fda085"),
        fill="tozeroy",
        fillcolor="rgba(246,211,101,0.10)",
        hovertemplate="%{x|%H:%M:%S}<br><b>%{y} °C</b><extra></extra>",
    ), row=1, col=1)

    # — Humidity line
    fig.add_trace(go.Scatter(
        x=df["timestamp"], y=df["humidity"],
        mode="lines+markers",
        name="Humidity",
        line=dict(color="#38bdf8", width=2.5),
        marker=dict(size=5, color="#818cf8"),
        fill="tozeroy",
        fillcolor="rgba(56,189,248,0.10)",
        hovertemplate="%{x|%H:%M:%S}<br><b>%{y} %RH</b><extra></extra>",
    ), row=2, col=1)

    # DHT11 safe-range bands
    fig.add_hrect(y0=20, y1=35, row=1, col=1,
                  fillcolor="rgba(34,197,94,0.07)", line_width=0,
                  annotation_text="Normal range", annotation_position="top left",
                  annotation_font_color="#22c55e", annotation_font_size=11)
    fig.add_hrect(y0=40, y1=80, row=2, col=1,
                  fillcolor="rgba(34,197,94,0.07)", line_width=0,
                  annotation_text="Normal range", annotation_position="top left",
                  annotation_font_color="#22c55e", annotation_font_size=11)

    fig.update_layout(
        height=560,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(255,255,255,0.03)",
        font=dict(color="#d1d5db"),
        showlegend=False,
        margin=dict(l=10, r=10, t=40, b=10),
        xaxis2=dict(
            showgrid=True, gridcolor="rgba(255,255,255,0.07)",
            tickformat="%H:%M:%S", color="#9ca3af"
        ),
        xaxis=dict(
            showgrid=True, gridcolor="rgba(255,255,255,0.07)", color="#9ca3af"
        ),
        yaxis=dict(
            showgrid=True, gridcolor="rgba(255,255,255,0.07)",
            color="#9ca3af", range=[0, 55]
        ),
        yaxis2=dict(
            showgrid=True, gridcolor="rgba(255,255,255,0.07)",
            color="#9ca3af", range=[0, 100]
        ),
    )
    fig.update_annotations(font_size=13)

    st.plotly_chart(fig, use_container_width=True)

    # ── Raw data table ─────────────────────────────────────────────────────
    with st.expander("📋 Raw Data Table"):
        display = df[["id","timestamp","temperature","humidity"]].copy()
        display.columns = ["ID", "Timestamp", "Temperature (°C)", "Humidity (%)"]
        st.dataframe(
            display.sort_values("ID", ascending=False).reset_index(drop=True),
            use_container_width=True, hide_index=True
        )

# ── Last updated + auto-refresh ───────────────────────────────────────────────
st.caption(f"🕐 Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if auto_refresh:
    import time
    time.sleep(REFRESH_SEC)
    st.rerun()
