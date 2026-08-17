import streamlit as st
import datetime
import requests
import plotly.graph_objects as go

st.set_page_config(page_title="Hourly Report SCADA Dashboard", layout="wide")

# Updated Google Apps Script Deployment URL
WEB_APP_URL = "https://script.google.com/macros/s/AKfycbzJAe0UgQO6YALceN2CgpsCGgnhF5zCe0_u6vLTyCEQmJNu1kRKpMbAWA8n-w86p4o/exec"

# Styling
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #070b19 0%, #0f172a 50%, #081026 100%);
        color: #ffffff;
    }
    .metric-card {
        background: rgba(30, 41, 59, 0.7);
        border: 1px solid rgba(56, 189, 248, 0.3);
        border-radius: 10px;
        padding: 15px;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    }
    .status-badge {
        padding: 6px 14px;
        border-radius: 20px;
        font-weight: bold;
        font-size: 14px;
        display: inline-block;
        margin-top: 5px;
    }
    .status-running { background: rgba(0, 230, 118, 0.2); color: #00e676; border: 1px solid #00e676; }
    .status-downtime { background: rgba(255, 0, 85, 0.2); color: #ff0055; border: 1px solid #ff0055; }
    .status-startup { background: rgba(255, 179, 0, 0.2); color: #ffb300; border: 1px solid #ffb300; }
    .status-changeover { background: rgba(41, 182, 246, 0.2); color: #29b6f6; border: 1px solid #29b6f6; }
</style>
""", unsafe_allow_html=True)

# Helper function for gauges
def build_gauge(title, value, color="#00e676"):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title={'text': title, 'font': {'size': 16, 'color': '#ffffff'}},
        number={'font': {'color': '#ffffff', 'size': 24}, 'suffix': "%"},
        gauge={
            'axis': {'range': [0, 100], 'tickcolor': "#ffffff"},
            'bar': {'color': color},
            'bgcolor': "rgba(15, 23, 42, 0.6)",
            'bordercolor': "#334155"
        }
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=220,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    return fig

# Initialize Session State
if 'live_data' not in st.session_state:
    st.session_state.live_data = {
        "line": "Liquid Line 1",
        "batch": "145730",
        "item": "SAMBUCOL LIQUID",
        "status": "Running",
        "reason": "N/A",
        "run_rate": 0,
        "duration_min": 0,
        "cumulative_units": 0
    }

st.markdown("<h2 style='text-align: center; color: #38bdf8; font-weight: 800;'>📋 HOURLY PRODUCTION REPORT</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #94a3b8;'>Real-time Line & Status Duration Tracker</p>", unsafe_allow_html=True)
st.markdown("---")

# --- LIVE METRICS OVERVIEW ---
st.markdown("### ⚡ Live Shift Overview")
m1, m2, m3, m4 = st.columns(4)

with m1:
    st.markdown(f"""
    <div class="metric-card">
        <div style="color: #94a3b8; font-size: 13px;">PRODUCTION LINE & ITEM</div>
        <div style="font-size: 18px; font-weight: bold; color: #ffffff; margin-top: 5px;">📍 {st.session_state.live_data['line']}</div>
        <div style="font-size: 12px; color: #38bdf8;">Item: {st.session_state.live_data['item']}</div>
        <div style="font-size: 11px; color: #64748b;">Batch: {st.session_state.live_data['batch']}</div>
    </div>
    """, unsafe_allow_html=True)

with m2:
    status_curr = st.session_state.live_data['status']
    badge_key = status_curr.lower().replace(" ", "")
    badge_cls = f"status-{badge_key}"
    st.markdown(f"""
    <div class="metric-card">
        <div style="color: #94a3b8; font-size: 13px;">CURRENT STATUS</div>
        <div class="status-badge {badge_cls}">{status_curr}</div>
        <div style="font-size: 11px; color: #94a3b8; margin-top: 5px;">Reason: {st.session_state.live_data['reason']}</div>
    </div>
    """, unsafe_allow_html=True)

with m3:
    st.markdown(f"""
    <div class="metric-card">
        <div style="color: #94a3b8; font-size: 13px;">LAST STATUS DURATION</div>
        <div style="font-size: 24px; font-weight: bold; color: #ffb300; margin-top: 2px;">⏱️ {st.session_state.live_data['duration_min']} <span style="font-size: 12px;">Mins</span></div>
    </div>
    """, unsafe_allow_html=True)

with m4:
    st.markdown(f"""
    <div class="metric-card">
        <div style="color: #94a3b8; font-size: 13px;">LIVE RUN RATE</div>
        <div style="font-size: 24px; font-weight: bold; color: #00e676; margin-top: 2px;">⚡ {st.session_state.live_data['run_rate']} <span style="font-size: 12px;">Units/Hr</span></div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# --- GAUGES SECTION ---
st.markdown("### 📊 Performance Indicators")
g1, g2, g3 = st.columns(3)
with g1:
    st.plotly_chart(build_gauge("Availability OEE", 92, "#00e676"), key="gauge_oee_avail")
with g2:
    st.plotly_chart(build_gauge("Performance OEE", 88, "#38bdf8"), key="gauge_oee_perf")
with g3:
    st.plotly_chart(build_gauge("Quality Yield", 98, "#ffb300"), key="gauge_oee_qual")

st.markdown("---")

# --- FORM SECTION ---
st.markdown("### 📝 Submit Hourly Entry")

c1, c2, c3 = st.columns(3)
line_input = c1.text_input("LINE", value="Liquid Line 1")
batch_input = c2.text_input("Batch", value="145730")
item_input = c3.text_input("Item", value="SAMBUCOL LIQUID")

c4, c5 = st.columns(2)
status_input = c4.selectbox("STATUS", ["Running", "Downtime", "Change Over", "Startup"])

reason_input = "N/A"
units_input = 0

if status_input in ["Downtime", "Change Over"]:
    reason_input = c5.text_input("Reason (Required for Downtime / Change Over)", value="Maintenance Check")
else:
    units_input = c5.number_input("Cumulative Units (For Running/Startup Calculation)", min_value=0, value=1000, step=50)

if st.button("Submit Hourly Log", use_container_width=True):
    payload = {
        "line": line_input,
        "batch": batch_input,
        "item": item_input,
        "status": status_input,
        "reason": reason_input,
        "units_done": units_input
    }
    
    try:
        res = requests.post(WEB_APP_URL, json=payload, timeout=5)
        if res.status_code == 200:
            data = res.json()
            if data.get("result") == "success":
                st.session_state.live_data = {
                    "line": line_input,
                    "batch": batch_input,
                    "item": item_input,
                    "status": status_input,
                    "reason": reason_input,
                    "run_rate": data.get("run_rate", 0),
                    "duration_min": data.get("duration_min", 0),
                    "cumulative_units": units_input
                }
                st.success(f"Log Updated! Status Duration: {data.get('duration_min')} Minutes.")
                st.rerun()
            else:
                st.error(f"Backend Error: {data.get('message')}")
        else:
            st.error("Failed to connect to Google Apps Script.")
    except Exception as e:
        st.error(f"Connection Error: {e}")
