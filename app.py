import streamlit as st
import datetime
import requests

st.set_page_config(page_title="SCADA Multi-Line Operations", layout="wide")

# Updated Web App URL
WEB_APP_URL = "https://script.google.com/macros/s/AKfycbzJAe0UgQO6YALceN2CgpsCGgnhF5zCe0_u6vLTyCEQmJNu1kRKpMbAWA8n-w86p4o/exec"

st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #070b19 0%, #0f172a 50%, #081026 100%); color: #ffffff; }
    .line-card { background: rgba(30, 41, 59, 0.85); border: 1px solid rgba(56, 189, 248, 0.4); border-radius: 12px; padding: 16px; margin-bottom: 10px; }
    .status-badge { padding: 5px 14px; border-radius: 15px; font-weight: bold; font-size: 13px; }
    .status-startup { background: rgba(255, 179, 0, 0.25); color: #ffb300; border: 1px solid #ffb300; }
    .status-running { background: rgba(0, 230, 118, 0.25); color: #00e676; border: 1px solid #00e676; }
    .status-changeover { background: rgba(41, 182, 246, 0.25); color: #29b6f6; border: 1px solid #29b6f6; }
    .status-downtime { background: rgba(255, 0, 85, 0.25); color: #ff0055; border: 1px solid #ff0055; }
</style>
""", unsafe_allow_html=True)

FACTORY_LINES = ["Liquid Line 1", "Liquid Line 2", "Liquid Line 3", "Powder Filling", "Cream", "Skyline", "Softgel"]

if 'lines_data' not in st.session_state:
    st.session_state.lines_data = {
        line: {
            "task": f"Task - {line}", "batch": "B-001", "target": 5000,
            "done": 0, "status": "Startup", "badge": "EMP-001", "updated": "N/A"
        } for line in FACTORY_LINES
    }

st.markdown("<h2 style='text-align: center; color: #38bdf8;'>🏭 Multi-Line SCADA Control Dashboard</h2>", unsafe_allow_html=True)

for line_name in FACTORY_LINES:
    d = st.session_state.lines_data[line_name]
    pct = min(100.0, (d["done"] / d["target"]) * 100) if d["target"] > 0 else 0
    
    st.markdown(f"""
    <div class="line-card">
        <div style="display: flex; justify-content: space-between;">
            <h3 style="margin:0; color:#38bdf8;">📍 {line_name}</h3>
            <span class="status-badge status-{d['status'].lower()}">Status: {d['status']}</span>
        </div>
        <div style="font-size: 13px; color: #cbd5e1; margin-top: 5px;">
            📋 Task: {d['task']} | Batch: {d['batch']} | OpID: {d['badge']} | Last: {d['updated']}
        </div>
    </div>
    """, unsafe_allow_html=True)

    cols = st.columns([1, 1, 1, 1])
    cols[0].metric("Target", f"{d['target']:,}")
    cols[1].metric("Done", f"{d['done']:,}")
    cols[2].metric("Left", f"{max(0, d['target'] - d['done']):,}")
    cols[3].metric("Progress", f"{pct:.1f}%")
    st.progress(pct / 100.0)

    with st.expander(f"⚙️ Settings & Actions ({line_name})"):
        c1, c2, c3, c4, c5 = st.columns(5)
        new_task = c1.text_input("Task", value=d["task"], key=f"t_{line_name}")
        new_batch = c2.text_input("Batch", value=d["batch"], key=f"b_{line_name}")
        new_target = c3.number_input("Target", value=d["target"], key=f"tg_{line_name}")
        new_done = c4.number_input("Done", value=d["done"], key=f"dn_{line_name}")
        new_badge = c5.text_input("Badge", value=d["badge"], key=f"id_{line_name}")

        b1, b2, b3, b4 = st.columns(4)
        
        def push_update(stat, task, bat, tar, don, bad):
            now = datetime.datetime.now().strftime("%H:%M:%S")
            payload = {"line": line_name, "task": task, "batch": bat, "status": stat, "units_done": don, "units_left": max(0, tar-don), "badge_no": bad, "timestamp": now}
            try:
                requests.post(WEB_APP_URL, json=payload, timeout=3)
                st.session_state.lines_data[line_name].update({"status": stat, "task": task, "batch": bat, "target": tar, "done": don, "badge": bad, "updated": now})
                st.rerun()
            except:
                st.error("Connection Failed!")

        if b1.button("STARTUP", key=f"st_{line_name}", use_container_width=True): push_update("Startup", new_task, new_batch, new_target, new_done, new_badge)
        if b2.button("RUNNING", key=f"rn_{line_name}", use_container_width=True): push_update("Running", new_task, new_batch, new_target, new_done, new_badge)
        if b3.button("CHANGEOVER", key=f"ch_{line_name}", use_container_width=True): push_update("Changeover", new_task, new_batch, new_target, new_done, new_badge)
        if b4.button("DOWNTIME", key=f"dt_{line_name}", use_container_width=True): push_update("Downtime", new_task, new_batch, new_target, new_done, new_badge)
    
    st.markdown("<br>", unsafe_allow_html=True)
