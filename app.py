import streamlit as st
import datetime
import requests
import plotly.graph_objects as go

st.set_page_config(page_title="Manufacturing Dashboard", layout="wide", initial_sidebar_state="collapsed")

# ====== CONFIG ======
WEB_APP_URL = "https://script.google.com/macros/s/AKfycbzJAe0UgQO6YALceN2CgpsCGgnhF5zCe0_u6vLTyCEQmJNu1kRKpMbAWA8n-w86p4o/exec"
FACTORY_LINES = ["Liquid Line 1", "Liquid Line 2", "Liquid Line 3", "Powder Filling", "Cream", "Skyline", "Softgel"]

# ====== CSS ======
st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #070b19 0%, #0f172a 50%, #081026 100%); color: #ffffff; }
    .line-card { background: rgba(30, 41, 59, 0.85); border: 1px solid rgba(56, 189, 248, 0.4); border-radius: 12px; padding: 16px; margin-bottom: 15px; }
    .status-badge { padding: 5px 14px; border-radius: 15px; font-weight: bold; font-size: 13px; }
    .status-startup { background: rgba(255, 179, 0, 0.25); color: #ffb300; border: 1px solid #ffb300; }
    .status-running { background: rgba(0, 230, 118, 0.25); color: #00e676; border: 1px solid #00e676; }
    .status-changeover { background: rgba(41, 182, 246, 0.25); color: #29b6f6; border: 1px solid #29b6f6; }
    .status-downtime { background: rgba(255, 0, 85, 0.25); color: #ff0055; border: 1px solid #ff0055; }
    .next-batch-box { background: rgba(56, 189, 248, 0.1); border-left: 3px solid #38bdf8; padding: 6px 12px; margin-top: 8px; border-radius: 4px; font-size: 13px; }
    .stButton>button { border-radius: 8px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# ====== SESSION STATE INIT ======
if 'lines_data' not in st.session_state:
    st.session_state.lines_data = {
        line: {
            "task": f"Task - {line}", "batch": "B-1001", "next_batch_name": "PENTAVITE", "next_batch_no": "123977",
            "target": 5000, "done": 1200, "status": "Startup", "badge": "EMP-101", "updated": "N/A"
        } for line in FACTORY_LINES
    }

# ====== GOOGLE SHEET SYNC FUNCTION ======
def sync_to_sheet(payload):
    try:
        # allow_redirects=False is MUST for Apps Script
        res = requests.post(WEB_APP_URL, json=payload, headers={"Content-Type": "application/json"}, timeout=10, allow_redirects=False)
        res.raise_for_status()
        data = res.json()
        return data.get("result") == "success", data.get("message")
    except requests.exceptions.RequestException as e:
        return False, str(e)

# ====== UPDATE FUNCTION ======
def push_update(line_name, new_data, stat):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") # Pakistan time format
    
    units_left = max(0, new_data["target"] - new_data["done"])
    
    payload = {
        "line": line_name, 
        "task": new_data["task"], 
        "batch": new_data["batch"],
        "next_batch_name": new_data["next_batch_name"], 
        "next_batch_no": new_data["next_batch_no"],
        "status": stat, 
        "units_done": new_data["done"], 
        "units_left": units_left,
        "badge_no": new_data["badge"], 
        "timestamp": now
    }
    
    # Local update first for instant UI
    st.session_state.lines_data[line_name].update({
        "status": stat, **new_data, "updated": now
    })

    # Sync to Google Sheet
    success, msg = sync_to_sheet(payload)
    if success:
        st.success("✅ Synced to Google Sheet successfully!")
    else:
        st.warning(f"⚠️ Local update done. Sheet sync failed: {msg}")
    
    st.rerun()

# ====== HEADER ======
st.markdown("<h2 style='text-align: center; color: #38bdf8;'>🏭 Manufacturing Dashboard - Live SCADA</h2>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align: center; color: #94a3b8;'>Last Refresh: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>", unsafe_allow_html=True)

# ====== MAIN LOOP FOR EACH LINE ======
for line_name in FACTORY_LINES:
    d = st.session_state.lines_data[line_name]
    pct = min(100.0, (d["done"] / d["target"]) * 100) if d["target"] > 0 else 0
    status_class = f"status-{d['status'].lower()}"
    
    # LINE CARD
    st.markdown(f"""
    <div class="line-card">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <h3 style="margin:0; color:#38bdf8;">📍 {line_name}</h3>
            <span class="status-badge {status_class}">Status: {d['status']}</span>
        </div>
        <div style="font-size: 13px; color: #cbd5e1; margin-top: 6px;">
            📋 <b>Current Task:</b> {d['task']} | <b>Current Batch #:</b> {d['batch']} | <b>Operator:</b> {d['badge']} | <b>Last Sync:</b> {d['updated']}
        </div>
        <div class="next-batch-box">
            ⏭️ <b>Next Batch Scheduled:</b> <span style="color:#38bdf8; font-weight:bold;">{d['next_batch_name']}</span> (Batch #: <b>{d['next_batch_no']}</b>)
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([3, 1])
    
    with col1:
        m1, m2, m3 = st.columns(3)
        m1.metric("Target Units", f"{d['target']:,}")
        m2.metric("Completed Units", f"{d['done']:,}")
        m3.metric("Units Left", f"{max(0, d['target'] - d['done']):,}")
        st.progress(pct / 100.0)

    with col2:
        # Live Efficiency Gauge
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=round(pct, 1),
            number={'suffix': "%", 'font': {'size': 20, 'color': "#ffffff"}},
            gauge={
                'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#cbd5e1"},
                'bar': {'color': "#00e676" if pct > 70 else "#ffb300" if pct > 40 else "#ff0055"},
                'bgcolor': "rgba(15, 23, 42, 0.5)",
                'bordercolor': "#38bdf8",
            }
        ))
        fig.update_layout(margin=dict(l=10, r=10, t=10, b=10), height=120, paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)

    # EXPANDER FOR CONTROLS
    with st.expander(f"⚙️ Task Assigner & Actions ({line_name})"):
        st.markdown("**1. Current & Next Batch Setup**")
        c1, c2, c3, c4 = st.columns(4)
        new_task = c1.text_input("Current Task", value=d["task"], key=f"t_{line_name}")
        new_batch = c2.text_input("Current Batch No", value=d["batch"], key=f"b_{line_name}")
        new_next_name = c3.text_input("Next Batch Name", value=d["next_batch_name"], key=f"nbn_{line_name}")
        new_next_no = c4.text_input("Next Batch No", value=d["next_batch_no"], key=f"nb_{line_name}")

        c5, c6, c7 = st.columns(3)
        new_target = c5.number_input("Target Units", value=d["target"], min_value=0, key=f"tg_{line_name}")
        new_done = c6.number_input("Units Completed", value=d["done"], min_value=0, key=f"dn_{line_name}")
        new_badge = c7.text_input("Operator Badge ID", value=d["badge"], key=f"id_{line_name}")
        
        new_data = {"task": new_task, "batch": new_batch, "next_batch_name": new_next_name, 
                    "next_batch_no": new_next_no, "target": new_target, "done": new_done, "badge": new_badge}

        st.markdown("**2. Action Status Buttons**")
        b1, b2, b3, b4 = st.columns(4)
        
        if b1.button("STARTUP", key=f"st_{line_name}", use_container_width=True, type="primary"): 
            push_update(line_name, new_data, "Startup")
        if b2.button("RUNNING", key=f"rn_{line_name}", use_container_width=True): 
            push_update(line_name, new_data, "Running")
        if b3.button("CHANGEOVER", key=f"ch_{line_name}", use_container_width=True): 
            push_update(line_name, new_data, "Changeover")
        if b4.button("DOWNTIME", key=f"dt_{line_name}", use_container_width=True): 
            push_update(line_name, new_data, "Downtime")
    
    st.markdown("<hr style='border-color: rgba(255,255,255,0.1);'>", unsafe_allow_html=True)
