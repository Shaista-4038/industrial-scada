import streamlit as st
import plotly.graph_objects as go
import datetime
import requests

# Page Configuration
st.set_page_config(page_title="Industrial SCADA Dashboard", layout="wide")

# Dark Glassmorphism Styling
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #070b19 0%, #0f172a 50%, #081026 100%);
        color: #ffffff;
    }
    .tank-card {
        background: rgba(30, 41, 59, 0.6);
        border: 1px solid rgba(56, 189, 248, 0.3);
        border-radius: 10px;
        padding: 12px;
        text-align: center;
        margin-bottom: 10px;
    }
    .badge {
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 11px;
        font-weight: 700;
        display: inline-block;
        margin-top: 6px;
    }
    .badge-mixing { background: rgba(0, 230, 118, 0.2); color: #00e676; border: 1px solid #00e676; }
    .badge-cip { background: rgba(255, 179, 0, 0.2); color: #ffb300; border: 1px solid #ffb300; }
    .badge-holding { background: rgba(41, 182, 246, 0.2); color: #29b6f6; border: 1px solid #29b6f6; }
    .badge-idle { background: rgba(229, 57, 53, 0.2); color: #ff5252; border: 1px solid #ff5252; }
    .badge-fault { background: rgba(255, 0, 85, 0.3); color: #ff0055; border: 1px solid #ff0055; }
</style>
""", unsafe_allow_html=True)

# Google Apps Script Endpoint
WEB_APP_URL = "https://script.google.com/macros/s/AKfycbzJAe0UgQO6YALceN2CgpsCGgnhF5zCe0_u6vLTyCEQmJNu1kRKpMbAWA8n-w86p4o/exec"

def send_to_gsheet(data):
    try:
        response = requests.post(WEB_APP_URL, json=data, timeout=5)
        return response.status_code == 200
    except Exception:
        return False

# Header
st.markdown("<h2 style='text-align: center; color: #38bdf8; font-weight: 800;'>🏭 INDUSTRIAL SCADA & CIP CONTROL CENTER</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #94a3b8;'>Real-time Process Monitoring • Live Google Sheets Telemetry</p>", unsafe_allow_html=True)

# State Management
if 'tank_status' not in st.session_state:
    st.session_state.tank_status = {
        f"Tank {i}": {"status": "Idle", "level": 2200, "fill": 15} for i in range(1, 11)
    }
    st.session_state.tank_status["Tank 1"] = {"status": "Mixing", "level": 2200, "fill": 75}
    st.session_state.tank_status["Tank 2"] = {"status": "CIP / Cleaning", "level": 2200, "fill": 40}
    st.session_state.tank_status["Tank 3"] = {"status": "CIP / Cleaning", "level": 2200, "fill": 40}
    st.session_state.tank_status["Tank 4"] = {"status": "Holding", "level": 2200, "fill": 75}
    st.session_state.tank_status["Tank 6"] = {"status": "Mixing", "level": 2200, "fill": 75}

if 'last_logged' not in st.session_state:
    st.session_state.last_logged = None

# --- TOP SECTION: 10 TANKS ---
st.markdown("#### Vessel Fleet Status")

cols = st.columns(10)
for idx, (tank_name, details) in enumerate(st.session_state.tank_status.items()):
    with cols[idx]:
        status = details.get("status", "Idle")
        fill_val = details.get("fill", 15)
        
        badge_class = "badge-cip" if status == "CIP / Cleaning" else f"badge-{status.lower()}"
        
        st.markdown(f"""
        <div class="tank-card">
            <div style="font-weight: 700; color: #f8fafc; font-size: 13px;">{tank_name}</div>
            <span class="badge {badge_class}">{status.split(' ')[0]}</span>
            <div style="font-size: 11px; color: #94a3b8; margin-top: 8px;">Capacity: 2,200L</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Native Industrial Progress Bar
        st.progress(fill_val / 100)

st.markdown("<br>", unsafe_allow_html=True)

# --- MIDDLE SECTION: GAUGES ---
m1, m2, m3, m4 = st.columns(4)

def build_gauge(title, value, color_hex):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        number={'suffix': "%", 'font': {'color': 'white', 'size': 22}},
        title={'text': title, 'font': {'color': '#94a3b8', 'size': 14}},
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': color_hex},
            'bgcolor': "rgba(30, 41, 59, 0.5)",
            'border': {'color': "rgba(255,255,255,0.1)"}
        }
    ))
    fig.update_layout(
        height=170,
        margin=dict(l=20, r=20, t=30, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )
    return fig

with m1:
    st.plotly_chart(build_gauge("Availability OEE", 92, "#00e676"), use_container_width=True)
with m2:
    st.plotly_chart(build_gauge("Performance", 88, "#ffb300"), use_container_width=True)
with m3:
    st.plotly_chart(build_gauge("Quality Standard", 99, "#29b6f6"), use_container_width=True)
with m4:
    st.plotly_chart(build_gauge("Batch Yield", 97.6, "#38bdf8"), use_container_width=True)

st.markdown("---")

# --- BOTTOM SECTION: AUTO-SYNC CONTROL PANEL ---
st.markdown("#### Auto-Sync Operational Control Panel")

c1, c2, c3, c4 = st.columns(4)

selected_tank = c1.selectbox("Select Tank", list(st.session_state.tank_status.keys()))
current_status = st.session_state.tank_status[selected_tank].get("status", "Idle")
status_list = ["Mixing", "CIP / Cleaning", "Holding", "Idle", "FAULT"]

selected_index = status_list.index(current_status) if current_status in status_list else 3
operation = c2.selectbox("Set Operation Status", status_list, index=selected_index)
operator = c3.text_input("Operator Name", "Shaista Haris")
duration = c4.text_input("Shift Notes", "12 Hours Shift")

# Auto-Sync Logic
current_state = (selected_tank, operation, operator, duration)

if st.session_state.tank_status[selected_tank].get("status") != operation or st.session_state.last_logged != current_state:
    new_fill = 75 if operation in ["Mixing", "Holding"] else (40 if operation == "CIP / Cleaning" else 15)
    st.session_state.tank_status[selected_tank]["status"] = operation
    st.session_state.tank_status[selected_tank]["fill"] = new_fill
    st.session_state.last_logged = current_state
    
    payload = {
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "unit_name": selected_tank,
        "operator_name": operator,
        "task_description": f"Auto-Logged: Status changed to {operation}",
        "duration": duration,
        "status": operation
    }
    
    if send_to_gsheet(payload):
        st.toast(f"⚡ Instant Sync: {selected_tank} set to {operation} & logged to Google Sheet!", icon="✅")
