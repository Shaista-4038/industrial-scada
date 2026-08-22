import streamlit as st
import datetime
import requests
import plotly.graph_objects as go

st.set_page_config(page_title="Manufacturing Dashboard", layout="wide")

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
    .priority-tag { padding: 4px 10px; border-radius: 6px; font-weight: bold; font-size: 12px; display: inline-block; }
    .next-batch-box { background: rgba(56, 189, 248, 0.1); border-left: 3px solid #38bdf8; padding: 6px 12px; margin-top: 8px; border-radius: 4px; font-size: 13px; }
</style>
""", unsafe_allow_html=True)

FACTORY_LINES = ["Liquid Line 1", "Liquid Line 2", "Liquid Line 3", "Powder Filling", "Cream", "Skyline", "Softgel"]

# Task Pool for Self-Assignment
if 'available_tasks' not in st.session_state:
    st.session_state.available_tasks = [
        {"task": "Bottle Washing & Sterilization", "batch": "B-9001", "priority": "🟠 High (Orange)"},
        {"task": "Syrup Blending & Filtering", "batch": "B-9002", "priority": "🟡 Medium (Yellow)"},
        {"task": "Cap Sealing & Inspection", "batch": "B-9003", "priority": "🟢 Normal (Green)"},
        {"task": "Labeling & Packaging Check", "batch": "B-9004", "priority": "🟢 Normal (Green)"}
    ]

if 'lines_data' not in st.session_state:
    st.session_state.lines_data = {
        line: {
            "task": "Unassigned Task", "batch": "N/A", "next_batch_name": "PENTAVITE", "next_batch_no": "123977",
            "target": 5000, "done": 0, "status": "Startup", "badge": "Unassigned", 
            "priority": "🟢 Normal (Green)", "start_time": "N/A", 
            "duration": "0 mins", "updated": "N/A"
        } for line in FACTORY_LINES
    }

st.markdown("<h2 style='text-align: center; color: #38bdf8;'>🏭 Manufacturing Execution Dashboard</h2>", unsafe_allow_html=True)

PRIORITY_COLORS = {
    "🟢 Normal (Green)": "background: rgba(0, 230, 118, 0.2); color: #00e676; border: 1px solid #00e676;",
    "🟡 Medium (Yellow)": "background: rgba(255, 235, 59, 0.2); color: #ffeb3b; border: 1px solid #ffeb3b;",
    "🟠 High (Orange)": "background: rgba(255, 152, 0, 0.2); color: #ff9800; border: 1px solid #ff9800;"
}

for line_name in FACTORY_LINES:
    d = st.session_state.lines_data[line_name]
    pct = min(100.0, (d["done"] / d["target"]) * 100) if d["target"] > 0 else 0
    p_style = PRIORITY_COLORS.get(d["priority"], PRIORITY_COLORS["🟢 Normal (Green)"])
    
    st.markdown(f"""
    <div class="line-card">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <h3 style="margin:0; color:#38bdf8;">📍 {line_name}</h3>
            <div>
                <span class="priority-tag" style="{p_style}">Priority: {d['priority']}</span>
                <span class="status-badge status-{d['status'].lower()}">Status: {d['status']}</span>
            </div>
        </div>
        <div style="font-size: 13px; color: #cbd5e1; margin-top: 6px;">
            📋 <b>Current Task:</b> {d['task']} | <b>Batch #:</b> {d['batch']} | 👤 <b>Operator ID:</b> <span style="color:#38bdf8; font-weight:bold;">{d['badge']}</span> | ⏱️ <b>Recorded Duration:</b> {d['duration']}
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
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=pct,
            number={'suffix': "%", 'font': {'size': 18, 'color': "#ffffff"}},
            gauge={
                'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#cbd5e1"},
                'bar': {'color': "#00e676" if pct > 70 else "#ffb300"},
                'bgcolor': "rgba(15, 23, 42, 0.5)",
                'bordercolor': "#38bdf8",
            }
        ))
        fig.update_layout(margin=dict(l=10, r=10, t=10, b=10), height=110, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True, key=f"gauge_{line_name}")

    with st.expander(f"⚙️ Task Management & Operator Panel ({line_name})"):
        st.markdown("**1. Select or Assign Task**")
        
        task_options = ["Custom Task Entry"] + [f"{t['task']} (Batch: {t['batch']})" for t in st.session_state.available_tasks]
        selected_pool_task = st.selectbox("Pick Unassigned Task from Queue", options=task_options, key=f"pool_{line_name}")

        c1, c2, c3 = st.columns(3)
        if selected_pool_task != "Custom Task Entry":
            chosen_item = next(t for t in st.session_state.available_tasks if f"{t['task']} (Batch: {t['batch']})" == selected_pool_task)
            new_task = c1.text_input("Active Task Name", value=chosen_item["task"], key=f"t_{line_name}")
            new_batch = c2.text_input("Current Batch No", value=chosen_item["batch"], key=f"b_{line_name}")
            new_priority = c3.text_input("Priority Level", value=chosen_item["priority"], key=f"p_{line_name}", disabled=True)
        else:
            new_task = c1.text_input("Active Task Name", value=d["task"], key=f"t_{line_name}")
            new_batch = c2.text_input("Current Batch No", value=d["batch"], key=f"b_{line_name}")
            new_priority = c3.selectbox("Task Priority Color", ["🟢 Normal (Green)", "🟡 Medium (Yellow)", "🟠 High (Orange)"], key=f"p_{line_name}")

        c4, c5 = st.columns(2)
        new_next_name = c4.text_input("Next Batch Name", value=d["next_batch_name"], key=f"nbn_{line_name}")
        new_next_no = c5.text_input("Next Batch No", value=d["next_batch_no"], key=f"nb_{line_name}")

        st.markdown("**2. Production Metrics & Action Logging**")
        c6, c7, c8 = st.columns(3)
        new_target = c6.number_input("Target Units", value=d["target"], key=f"tg_{line_name}")
        new_done = c7.number_input("Units Completed", value=d["done"], key=f"dn_{line_name}")
        new_badge = c8.text_input("Operator Badge ID", value=d["badge"] if d["badge"] != "Unassigned" else "", key=f"id_{line_name}")

        b1, b2, b3, b4 = st.columns(4)
        
        def push_update(stat):
            if not new_badge.strip() or new_badge == "Unassigned":
                st.error("Please enter a valid Operator Badge ID before updating status!")
                return
                
            now = datetime.datetime.now()
            now_str = now.strftime("%H:%M:%S")
            
            start_ref = d["start_time"] if d["start_time"] != "N/A" else now_str
            
            try:
                start_dt = datetime.datetime.strptime(start_ref, "%H:%M:%S").replace(year=now.year, month=now.month, day=now.day)
                duration_mins = round((now - start_dt).total_seconds() / 60, 1)
                duration_str = f"{duration_mins} mins"
            except:
                duration_str = "0 mins"

            payload = {
                "line": line_name, "task": new_task, "batch": new_batch,
                "priority": new_priority, "next_batch_name": new_next_name, "next_batch_no": new_next_no,
                "status": stat, "units_done": new_done, "units_left": max(0, new_target - new_done),
                "badge_no": new_badge, "timestamp": now_str, "duration": duration_str
            }
            
            st.session_state.lines_data[line_name].update({
                "status": stat, "task": new_task, "batch": new_batch, "priority": new_priority,
                "next_batch_name": new_next_name, "next_batch_no": new_next_no,
                "target": new_target, "done": new_done, "badge": new_badge, "updated": now_str,
                "duration": duration_str, "start_time": start_ref
            })

            try:
                requests.post(WEB_APP_URL, json=payload, headers={"Content-Type": "application/json"}, timeout=5, allow_redirects=True)
                st.success("Synced directly to Google Sheets!")
            except Exception:
                st.info("Updated locally on dashboard.")
            st.rerun()

        if b1.button("STARTUP", key=f"st_{line_name}", use_container_width=True): push_update("Startup")
        if b2.button("RUNNING", key=f"rn_{line_name}", use_container_width=True): push_update("Running")
        if b3.button("CHANGEOVER", key=f"ch_{line_name}", use_container_width=True): push_update("Changeover")
        if b4.button("DOWNTIME", key=f"dt_{line_name}", use_container_width=True): push_update("Downtime")
    
    st.markdown("<hr style='border-color: rgba(255,255,255,0.1);'>", unsafe_allow_html=True)
