import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import datetime
import requests

# Page Configuration (Industrial Dark Theme)
st.set_page_config(page_title="SCADA Industrial Dashboard", layout="wide")

# Custom Industrial SCADA Styling
st.markdown("""
<style>
    .stApp { background-color: #0b111e; color: #ffffff; }
    .tank-card {
        background: #151c2c;
        border: 1px solid #28354a;
        border-radius: 8px;
        padding: 10px;
        text-align: center;
        margin-bottom: 8px;
    }
    .status-badge {
        padding: 4px 8px;
        border-radius: 4px;
        font-weight: bold;
        font-size: 12px;
        display: inline-block;
        margin-top: 4px;
    }
    .status-mixing { background-color: #00e676; color: #000; }
    .status-cip { background-color: #ffb300; color: #000; }
    .status-holding { background-color: #29b6f6; color: #000; }
    .status-idle { background-color: #e53935; color: #fff; }
</style>
""", unsafe_allow_html=True)

# Google Apps Script Web App Endpoint
WEB_APP_URL = "https://script.google.com/macros/s/AKfycbzJAe0UgQO6YALceN2CgpsCGgnhF5zCe0_u6vLTyCEQmJNu1kRKpMbAWA8n-w86p4o/exec"

def send_to_gsheet(data):
    try:
        response = requests.post(WEB_APP_URL, json=data, timeout=5)
        return response.status_code == 200
    except Exception:
        return False

st.title("🏭 INDUSTRIAL CONTROL & CIP DASHBOARD")

# --- TOP SECTION: 10 VISUAL TANKS ---
st.markdown("### 🛢️ Vessel & Tank Monitoring")

if 'tank_status' not in st.session_state:
    st.session_state.tank_status = {
        f"Tank {i}": {"status": "Idle", "level": 2200, "ETA": "11:15"} for i in range(1, 11)
    }
    # Initial status presets matching the visual interface
    st.session_state.tank_status["Tank 1"]["status"] = "Mixing"
    st.session_state.tank_status["Tank 2"]["status"] = "CIP"
    st.session_state.tank_status["Tank 3"]["status"] = "CIP"
    st.session_state.tank_status["Tank 5"]["status"] = "Cleaning"
    st.session_state.tank_status["Tank 6"]["status"] = "Holding"

cols = st.columns(10)
for idx, (tank_name, details) in enumerate(st.session_state.tank_status.items()):
    with cols[idx]:
        st.markdown(f"**{tank_name}**")
        status = details["status"]
        if status == "Mixing":
            badge_class = "status-mixing"
        elif status in ["CIP", "Cleaning"]:
            badge_class = "status-cip"
        elif status == "Holding":
            badge_class = "status-holding"
        else:
            badge_class = "status-idle"
            
        st.markdown(f'<div class="tank-card"><span class="status-badge {badge_class}">{status}</span></div>', unsafe_allow_html=True)
        st.caption(f"📦 {details['level']} L\nETA: {details['ETA']}")

st.markdown("---")

# --- MIDDLE SECTION: PERFORMANCE GAUGES ---
m1, m2, m3, m4 = st.columns(4)

with m1:
    fig1 = go.Figure(go.Indicator(
        mode="gauge+number", value=92, title={'text': "Availability (OEE)"},
        gauge={'axis': {'range': [0, 100]}, 'bar': {'color': "#00e676"}}
    ))
    fig1.update_layout(height=160, margin=dict(l=10, r=10, t=30, b=10), paper_bgcolor="#0b111e", font=dict(color="white"))
    st.plotly_chart(fig1, use_container_width=True)

with m2:
    fig2 = go.Figure(go.Indicator(
        mode="gauge+number", value=88, title={'text': "Performance"},
        gauge={'axis': {'range': [0, 100]}, 'bar': {'color': "#ffb300"}}
    ))
    fig2.update_layout(height=160, margin=dict(l=10, r=10, t=30, b=10), paper_bgcolor="#0b111e", font=dict(color="white"))
    st.plotly_chart(fig2, use_container_width=True)

with m3:
    fig3 = go.Figure(go.Indicator(
        mode="gauge+number", value=99, title={'text': "Quality"},
        gauge={'axis': {'range': [0, 100]}, 'bar': {'color': "#29b6f6"}}
    ))
    fig3.update_layout(height=160, margin=dict(l=10, r=10, t=30, b=10), paper_bgcolor="#0b111e", font=dict(color="white"))
    st.plotly_chart(fig3, use_container_width=True)

with m4:
    fig4 = go.Figure(go.Indicator(
        mode="gauge+number", value=97.6, title={'text': "Yield (%)"},
        gauge={'axis': {'range': [0, 100]}, 'bar': {'color': "#00e676"}}
    ))
    fig4.update_layout(height=160, margin=dict(l=10, r=10, t=30, b=10), paper_bgcolor="#0b111e", font=dict(color="white"))
    st.plotly_chart(fig4, use_container_width=True)

st.markdown("---")

# --- BOTTOM SECTION: REAL-TIME OPERATIONAL CONTROL PANEL ---
st.markdown("### 🎛️ Live Operation & Google Sheet Logging Panel")

c1, c2, c3, c4 = st.columns(4)

selected_tank = c1.selectbox("Select Tank", list(st.session_state.tank_status.keys()))
operation = c2.selectbox("Operation Status", ["Mixing", "CIP / Cleaning", "Holding", "Idle", "FAULT"])
operator = c3.text_input("Operator Name", "Shaista Haris")
duration = c4.text_input("Shift Duration / Notes", "12 Hours Shift")

if st.button("🚀 Push Update to Dashboard & Google Sheet"):
    # 1. Update UI Status locally
    st.session_state.tank_status[selected_tank]["status"] = operation
    
    # 2. Build Webhook Payload
    payload = {
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "unit_name": selected_tank,
        "operator_name": operator,
        "task_description": f"Status changed to {operation}",
        "duration": duration,
        "status": operation
    }
    
    # 3. Transmit data to Google Sheets via Webhook
    success = send_to_gsheet(payload)
    if success:
        st.success(f"✅ Status updated for {selected_tank} and logged to Google Sheets!")
    else:
        st.error("⚠️ Dashboard updated locally, but Google Sheets connection failed. Please verify Web App permissions.")
