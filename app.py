import streamlit as st
import plotly.graph_objects as go
import datetime
import requests

# Page Configuration
st.set_page_config(page_title="Industrial SCADA & CIP Control Center", layout="wide")

# Custom Glassmorphism Theme & UI Styling
st.markdown("""
<style>
    /* Dark & Blue Gradient Background */
    .stApp {
        background: linear-gradient(135deg, #070b19 0%, #0f172a 50%, #081026 100%);
        color: #ffffff;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }

    /* Outer Glass Panels */
    .glass-panel {
        background: rgba(15, 23, 42, 0.65);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(56, 189, 248, 0.2);
        border-radius: 12px;
        padding: 16px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
        margin-bottom: 20px;
    }

    /* Individual Tank Card */
    .tank-card {
        background: rgba(30, 41, 59, 0.5);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 8px;
        padding: 8px;
        text-align: center;
        transition: border 0.3s ease;
    }
    .tank-card:hover {
        border: 1px solid #38bdf8;
    }

    /* Dynamic Badges */
    .badge {
        padding: 3px 8px;
        border-radius: 12px;
        font-size: 11px;
        font-weight: 700;
        display: inline-block;
        margin-top: 4px;
    }
    .badge-mixing { background: rgba(0, 230, 118, 0.2); color: #00e676; border: 1px solid #00e676; }
    .badge-cip { background: rgba(255, 179, 0, 0.2); color: #ffb300; border: 1px solid #ffb300; }
    .badge-holding { background: rgba(41, 182, 246, 0.2); color: #29b6f6; border: 1px solid #29b6f6; }
    .badge-idle { background: rgba(229, 57, 53, 0.2); color: #ff5252; border: 1px solid #ff5252; }
    .badge-fault { background: rgba(255, 0, 85, 0.3); color: #ff0055; border: 1px solid #ff0055; box-shadow: 0 0 8px #ff0055; }
</style>
""", unsafe_allow_html=True)

# Google Apps Script Web App URL
WEB_APP_URL = "https://script.google.com/macros/s/AKfycbzJAe0UgQO6YALceN2CgpsCGgnhF5zCe0_u6vLTyCEQmJNu1kRKpMbAWA8n-w86p4o/exec"

def send_to_gsheet(data):
    try:
        response = requests.post(WEB_APP_URL, json=data, timeout=5)
        return response.status_code == 200
    except Exception:
        return False

# Function to render Realistic Metallic Cylindrical Tank
def render_metallic_tank(color, fill_pct):
    fill_height = int((fill_pct / 100) * 44)
    y_pos = 54 - fill_height
    return f"""
    <div style="width: 100%; max-width: 60px; margin: 0 auto;">
        <svg viewBox="0 0 60 70" width="100%" height="70">
            <!-- Metallic Top Cap -->
            <path d="M10 18 Q30 5 50 18 L50 20 L10 20 Z" fill="#64748b" stroke="#cbd5e0" stroke-width="1"/>
            <!-- Pipe inlet -->
            <rect x="27" y="2" width="6" height="6" fill="#94a3b8"/>
            <!-- Tank Body -->
            <rect x="10" y="20" width="40" height="36" rx="2" fill="#0f172a" stroke="#94a3b8" stroke-width="1.5"/>
            <!-- Liquid Level Fill -->
            <rect x="12" y="{y_pos}" width="36" height="{fill_height}" fill="{color}" opacity="0.85" rx="1"/>
            <!-- Metallic Base & Legs -->
            <path d="M10 56 Q30 61 50 56 L50 58 L10 58 Z" fill="#475569"/>
            <line x1="14" y1="58" x2="11" y2="67" stroke="#cbd5e0" stroke-width="2"/>
            <line x1="46" y1="58" x2="49" y2="67" stroke="#cbd5e0" stroke-width="2"/>
        </svg>
    </div>
    """

# Header Title
st.markdown("<h2 style='text-align: center; color: #ffffff; font-weight: 800; letter-spacing: 1px;'>🏭 INDUSTRIAL SCADA & CIP CONTROL CENTER</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #94a3b8; font-size: 14px;'>Real-time Process Monitoring • Live Google Sheets Telemetry</p>", unsafe_allow_html=True)

# Session State Initialization
if 'tank_status' not in st.session_state:
    st.session_state.tank_status = {
        f"Tank {i}": {"status": "Idle", "level": 2200, "fill": 15} for i in range(1, 11)
    }
    st.session_state.tank_status["Tank 1"] = {"status": "Mixing", "level": 2200, "fill": 75}
    st.session_state.tank_status["Tank 2"] = {"status": "CIP / Cleaning", "level": 2200, "fill": 40}
    st.session_state.tank_status["Tank 3"] = {"status": "CIP / Cleaning", "level": 2200, "fill": 40}
    st.session_state.tank_status["Tank 4"] = {"status": "Holding", "level": 2200, "fill": 75}
    st.session_state.tank_status["Tank 6"] = {"status": "Mixing", "level": 2200, "fill": 75}
    st.session_state.tank_status["Tank 7"] = {"status": "Holding", "level": 2200, "fill": 75}
    st.session_state.tank_status["Tank 8"] = {"status": "Holding", "level": 2200, "fill": 75}

if 'last_logged' not in st.session_state:
    st.session_state.last_logged = None

# --- TOP PANEL: 10 VISUAL TANKS ---
st.markdown("#### Vessel Fleet Status")

cols = st.columns(10)
status_colors = {
    "Mixing": "#00e676",
    "CIP / Cleaning": "#ffb300",
    "Holding": "#29b6f6",
    "Idle": "#ff5252",
    "FAULT": "#ff0055"
}

for idx, (tank_name, details) in enumerate(st.session_state.tank_status.items()):
    with cols[idx]:
        status = details["status"]
        color = status_colors.get(status, "#ff5252")
        badge_type = "cip" if status == "CIP / Cleaning" else status.lower()
        
        tank_svg = render_metallic_tank(color, details["fill"])
        
        st.markdown(f"""
        <div class="tank-card">
            <div style="font-weight: 600; font-size: 13px; color: #f8fafc;">{tank_name}</div>
            {tank_svg}
            <span class="badge badge-{badge_type}">{status.split(' ')[0]}</span>
            <div style="font-weight: bold; font-size: 11px; color: #ffffff; margin-top: 4px;">{details['fill']}%</div>
            <div style="font-size: 10px; color: #64748b;">{details['level']} L</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# --- MIDDLE PANEL: CIRCULAR GAUGES ---
m1, m2, m3, m4 = st.columns(4)

def build_gauge(title, value, color):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        number={'suffix': "%", 'font': {'color': 'white', 'size': 24}},
        title={'text': title, 'font': {'color': '#94a3b8', 'size': 14}},
        gauge={
            'shape': "angular",
            'axis': {'range': [0, 100], 'visible': False},
            'bar': {'color': color, 'thickness': 0.28},
            'bgcolor': "rgba(255, 255, 255, 0.05)",
            'border': {'width': 0}
        }
    ))
    fig.update_layout(
        height=180,
        margin=dict(l=10, r=10, t=30, b=10),
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

# --- BOTTOM PANEL: AUTO-SYNC CONTROL PANEL ---
st.markdown("#### Auto-Sync Operational Control Panel")

c1, c2, c3, c4 = st.columns(4)

selected_tank = c1.selectbox("Select Tank", list(st.session_state.tank_status.keys()))
current_status = st.session_state.tank_status[selected_tank]["status"]
status_list = ["Mixing", "CIP / Cleaning", "Holding", "Idle", "FAULT"]

selected_index = status_list.index(current_status) if current_status in status_list else 3
operation = c2.selectbox("Set Operation Status", status_list, index=selected_index)
operator = c3.text_input("Operator Name", "Shaista Haris")
duration = c4.text_input("Shift Notes", "12 Hours Shift")

# AUTO-LOGIC: Instant sync without explicit button click
current_state = (selected_tank, operation, operator, duration)

if st.session_state.tank_status[selected_tank]["status"] != operation or st.session_state.last_logged != current_state:
    # Update Tank State
    st.session_state.tank_status[selected_tank]["status"] = operation
    st.session_state.tank_status[selected_tank]["fill"] = 75 if operation in ["Mixing", "Holding"] else (40 if operation == "CIP / Cleaning" else 15)
    st.session_state.last_logged = current_state
    
    # Telemetry Payload
    payload = {
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "unit_name": selected_tank,
        "operator_name": operator,
        "task_description": f"Auto-Logged: Status changed to {operation}",
        "duration": duration,
        "status": operation
    }
    
    # Send to Google Sheets
    if send_to_gsheet(payload):
        st.toast(f"⚡ Instant Sync: {selected_tank} set to {operation} & logged to Google Sheet!", icon="✅")
    else:
        st.toast("⚠️ Sync warning: Local UI updated, Google Sheet endpoint busy.", icon="⚠️")
