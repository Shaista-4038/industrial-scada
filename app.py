import streamlit as st
import pandas as pd
from datetime import datetime

# Dashboard Configuration
st.set_page_config(page_title="Industrial Control Dashboard", layout="wide")

st.markdown("<h2 style='text-align: center; color: #00E5FF;'>🏭 INDUSTRIAL CONTROL & CIP DASHBOARD</h2>", unsafe_allow_html=True)
st.divider()

# KPIs
col1, col2, col3, col4 = st.columns(4)
col1.metric("Availability (OEE)", "92%", "+2%")
col2.metric("Performance", "88%", "-1%")
col3.metric("Quality", "99%", "0%")
col4.metric("Overall Yield", "97.6%", "+0.5%")

st.divider()

# Controls
st.subheader("🕹️ Line & CIP Control Panel")
c1, c2, c3 = st.columns(3)

with c1:
    line_select = st.selectbox("Select Line / Tank", ["Tank 1 (Mixing)", "Tank 2 (CIP)", "Tank 3 (Idle)", "Filling Line 1"])
with c2:
    operator = st.selectbox("Operator Name", ["Ali Ahmed", "Usman Khan", "Sara Raza"])
with c3:
    current_hour = datetime.now().hour
    shift = "Night Shift" if (current_hour >= 20 or current_hour < 8) else "Day Shift"
    st.text_input("Auto Detected Shift", value=shift, disabled=True)

b1, b2, b3 = st.columns(3)
if b1.button("🚀 Start Batch"): st.success("Batch Started!")
if b2.button("🧼 Start CIP"): st.warning("CIP Initiated!")
if b3.button("🛑 Stop Line"): st.error("Line Stopped!")