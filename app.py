import streamlit as st
import datetime
import requests
import plotly.graph_objects as go

st.set_page_config(page_title="Hourly Production SCADA Dashboard", layout="wide")

# Active Web App Deployment URL
WEB_APP_URL = "https://script.google.com/macros/s/AKfycbzJAe0UgQO6YALceN2CgpsCGgnhF5zCe0_u6vLTyCEQmJNu1kRKpMbAWA8n-w86p4o/exec"

st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #070b19 0%, #0f172a 50%, #081026 100%);
        color: #ffffff;
    }
    .metric-card {
        background: rgba(30, 41, 59, 0.7);
        border: 1px solid rgba(56, 189, 248, 0.3);
        border-radius: 12px;
        padding: 16px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.4);
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

def build_gauge(title, value, color="#00e676"):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title={'text': title, 'font': {'size': 16, 'color': '#ffffff'}},
        number={'font': {'color': '#ffffff', 'size': 26}, 'suffix': "%"},
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
        height=200,
        margin=dict(l=20, r=20, t=30, b=20)
    )
    return fig

default_state = {
    "line": "Liquid Line 1",
    "batch": "145730",
    "item": "SAMBUCOL LIQUID",
    "status": "Running",
    "reason": "N/A",
    "selected_time": "08:00",
    "current_run_rate": 0,
    "avg_run_rate": 0,
    "cumulative_units": 0,
    "avail_oee": 92,
    "perf_oee": 88,
    "quality_yield": 98
}

if 'live_data' not in st.session_state:
    st.session_state.live_data = default_state
else:
    for k, v in default_state.items():
        if k not in st.session_state.live_data:
            st.session_state.live_data[k] = v

st.markdown("<h2 style='text-align: center; color: #38bdf8; font-weight: 800;'>📊 Performance Indicators</h2>", unsafe_allow_html=True)

# 1. Dynamic OEE Gauges
g1, g2, g3 = st.columns(3)
with g1:
    st.plotly_chart(build_gauge("Availability OEE", st.session_state.live_data.get('avail_oee', 92), "#00e676"), key="gauge_avail")
with g2:
    st.plotly_chart(build_gauge("Performance OEE", st.session_state.live_data.get('perf_oee', 88), "#38bdf8"), key="gauge_perf")
with g3:
    st.plotly_chart(build_gauge("Quality Yield", st.session_state.live_data.get('quality_yield', 98), "#ffb300"), key="gauge_qual")

st.markdown("---")

# 2. Shift Metrics Display
st.markdown("### ⚡ Live Shift Analytics")
m1, m2, m3, m4, m5 = st.columns(5)

line_val = st.session_state.live_data.get('line', 'Liquid Line 1')
batch_val = st.session_state.live_data.get('batch', '145730')
item_val = st.session_state.live_data.get('item', 'SAMBUCOL LIQUID')
status_curr = st.session_state.live_data.get('status', 'Running')
time_val = st.session_state.live_data.get('selected_time', '08:00')
curr_rate = st.session_state.live_data.get('current_run_rate', 0)
avg_rate = st.session_state.live_data.get('avg_run_rate', 0)
cum_units = st.session_state.live_data.get('cumulative_units', 0)

with m1:
    st.markdown(f"""
    <div class="metric-card">
        <div style="color: #94a3b8; font-size: 12px;">LINE & BATCH</div>
        <div style="font-size: 15px; font-weight: bold; color: #ffffff; margin-top: 4px;">📍 {line_val}</div>
        <div style="font-size: 11px; color: #38bdf8;">Item: {item_val}</div>
        <div style="font-size: 10px; color: #64748b;">Batch: {batch_val}</div>
    </div>
    """, unsafe_allow_html=True)

with m2:
    badge_key = status_curr.lower().replace(" ", "")
    st.markdown(f"""
    <div class="metric-card">
        <div style="color: #94a3b8; font-size: 12px;">STATUS</div>
        <div class="status-badge status-{badge_key}">{status_curr}</div>
        <div style="font-size: 11px; color: #94a3b8; margin-top: 4px;">Time: {time_val}</div>
    </div>
    """, unsafe_allow_html=True)

with m3:
    st.markdown(f"""
    <div class="metric-card">
        <div style="color: #94a3b8; font-size: 12px;">CURRENT RUN RATE</div>
        <div style="font-size: 20px; font-weight: bold; color: #00e676; margin-top: 2px;">⚡ {curr_rate} <span style="font-size: 11px;">u/hr</span></div>
    </div>
    """, unsafe_allow_html=True)

with m4:
    st.markdown(f"""
    <div class="metric-card">
        <div style="color: #94a3b8; font-size: 12px;">AVERAGE RUN RATE</div>
        <div style="font-size: 20px; font-weight: bold; color: #38bdf8; margin-top: 2px;">📈 {avg_rate} <span style="font-size: 11px;">u/hr</span></div>
    </div>
    """, unsafe_allow_html=True)

with m5:
    st.markdown(f"""
    <div class="metric-card">
        <div style="color: #94a3b8; font-size: 12px;">CUMULATIVE UNITS</div>
        <div style="font-size: 20px; font-weight: bold; color: #ffb300; margin-top: 2px;">📦 {cum_units}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
st.markdown("---")

# 3. Submit Hourly Entry Section
st.markdown("### 📝 Submit Hourly Entry")

line_input = st.text_input("LINE", value=st.session_state.live_data.get('line', 'Liquid Line 1'))
batch_input = st.text_input("Batch", value=st.session_state.live_data.get('batch', '145730'))
item_input = st.text_input("Item", value=st.session_state.live_data.get('item', 'SAMBUCOL LIQUID'))

status_options = ["Running", "Downtime", "Change Over", "Startup"]
status_input = st.selectbox("STATUS", status_options)

c_time, c_units = st.columns(2)
with c_time:
    time_input = st.time_input("Select Time (24-hr format)", datetime.time(8, 0))
    formatted_time = time_input.strftime("%H:%M")

with c_units:
    units_input = st.number_input("Cumulative Units (For Running/Startup Calculation)", min_value=0, value=1000, step=50)

reason_input = "N/A"
if status_input in ["Downtime", "Change Over"]:
    reason_input = st.text_input("Reason (Required for Downtime/Change Over)", value="Maintenance Check")

if st.button("Submit Hourly Log", use_container_width=True):
    payload = {
        "line": line_input,
        "batch": batch_input,
        "item": item_input,
        "status": status_input,
        "reason": reason_input,
        "logged_time": formatted_time,
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
                    "selected_time": formatted_time,
                    "current_run_rate": data.get("current_run_rate", 0),
                    "avg_run_rate": data.get("avg_run_rate", 0),
                    "cumulative_units": units_input,
                    "avail_oee": data.get("avail_oee", 92),
                    "perf_oee": data.get("perf_oee", 88),
                    "quality_yield": data.get("quality_yield", 98)
                }
                st.success(f"Log Submitted! Current Run Rate: {data.get('current_run_rate')} u/hr | Avg Run Rate: {data.get('avg_run_rate')} u/hr")
                st.rerun()
            else:
                st.error(f"Backend Error: {data.get('message')}")
        else:
            st.error("Failed to connect to Google Apps Script.")
    except Exception as e:
        st.error(f"Network Error: {e}")
