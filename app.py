import streamlit as st
import datetime
import requests
import plotly.graph_objects as go

# Page Layout Configuration
st.set_page_config(page_title="Industrial SCADA & Live Run Rate Dashboard", layout="wide")

# Google Apps Script Web App Deployment URL
WEB_APP_URL = "https://script.google.com/macros/s/YOUR_EXEC_URL/exec"

# Custom SCADA Dark Theme Styling
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

# Helper Function for Safe Plotly Gauge Chart Rendering
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

# Initialize Dashboard Session State
if 'live_data' not in st.session_state:
    st.session_state.live_data = {
        "operator": "Ali",
        "status": "Running",
        "run_rate": 1100,
        "cumulative_units": 1800,
        "interval_units": 1100,
        "batch_no": "BN-2026-001"
    }

st.markdown("<h2 style='text-align: center; color: #38bdf8; font-weight: 800;'>🏭 INDUSTRIAL SCADA & LIVE RUN RATE DASHBOARD</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #94a3b8;'>Real-Time Telemetry & Production Analytics</p>", unsafe_allow_html=True)
st.markdown("---")

# --- TOP SECTION: LIVE OPERATOR & RUN RATE METRICS ---
st.markdown("### ⚡ Live Shift Overview")

m1, m2, m3, m4 = st.columns(4)

with m1:
    st.markdown(f"""
    <div class="metric-card">
        <div style="color: #94a3b8; font-size: 13px;">ACTIVE OPERATOR</div>
        <div style="font-size: 22px; font-weight: bold; color: #ffffff; margin-top: 5px;">👤 {st.session_state.live_data['operator']}</div>
        <div style="font-size: 11px; color: #64748b;">Batch: {st.session_state.live_data['batch_no']}</div>
    </div>
    """, unsafe_allow_html=True)

with m2:
    status_curr = st.session_state.live_data['status']
    badge_cls = f"status-{status_curr.lower()}"
    st.markdown(f"""
    <div class="metric-card">
        <div style="color: #94a3b8; font-size: 13px;">CURRENT LINE STATUS</div>
        <div class="status-badge {badge_cls}">{status_curr}</div>
    </div>
    """, unsafe_allow_html=True)

with m3:
    st.markdown(f"""
    <div class="metric-card">
        <div style="color: #94a3b8; font-size: 13px;">LIVE RUN RATE</div>
        <div style="font-size: 24px; font-weight: bold; color: #38bdf8; margin-top: 2px;">⚡ {st.session_state.live_data['run_rate']} <span style="font-size: 12px;">Units/Hr</span></div>
    </div>
    """, unsafe_allow_html=True)

with m4:
    st.markdown(f"""
    <div class="metric-card">
        <div style="color: #94a3b8; font-size: 13px;">TOTAL CUMULATIVE OUTPUT</div>
        <div style="font-size: 24px; font-weight: bold; color: #00e676; margin-top: 2px;">📦 {st.session_state.live_data['cumulative_units']} <span style="font-size: 12px;">Units</span></div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# --- MIDDLE SECTION: GAUGES SECTION (FIXED FOR PLOTLY ERRORS) ---
st.markdown("### 📊 Performance Indicators (OEE Gauges)")
g1, g2, g3 = st.columns(3)

with g1:
    st.plotly_chart(build_gauge("Availability OEE", 92, "#00e676"), key="gauge_oee_avail")
with g2:
    st.plotly_chart(build_gauge("Performance OEE", 88, "#38bdf8"), key="gauge_oee_perf")
with g3:
    st.plotly_chart(build_gauge("Quality Yield", 98, "#ffb300"), key="gauge_oee_qual")

st.markdown("---")

# --- BOTTOM SECTION: OPERATOR DATA ENTRY PANEL ---
st.markdown("### 🎛️ Operator Production Input Panel")

c1, c2, c3, c4 = st.columns(4)

operator_input = c1.text_input("Operator Name", value=st.session_state.live_data['operator'])
batch_number_input = c2.text_input("Batch Number", value=st.session_state.live_data['batch_no'])
status_input = c3.selectbox("Line Status", ["Running", "Downtime", "Startup", "Changeover"], index=["Running", "Downtime", "Startup", "Changeover"].index(st.session_state.live_data['status']))
units_input = c4.number_input("Cumulative Production Count", min_value=0, value=st.session_state.live_data['cumulative_units'], step=50)

if st.button("Submit Production Log", use_container_width=True):
    payload = {
        "operator_name": operator_input,
        "batch_number": batch_number_input,
        "status": status_input,
        "units_done": units_input
    }
    
    try:
        res = requests.post(WEB_APP_URL, json=payload, timeout=5)
        if res.status_code == 200:
            data = res.json()
            if data.get("result") == "success":
                st.session_state.live_data = {
                    "operator": operator_input,
                    "status": status_input,
                    "run_rate": data.get("run_rate", 0),
                    "cumulative_units": units_input,
                    "interval_units": data.get("interval_units", 0),
                    "batch_no": batch_number_input
                }
                st.success(f"Production Logged! Calculated Run Rate: {data.get('run_rate')} Units/Hr.")
                st.rerun()
            else:
                st.error(f"Backend Error: {data.get('message')}")
        else:
            st.error("Connection failed with Google Apps Script endpoint.")
    except Exception as e:
        st.error(f"Network Error: {e}")
