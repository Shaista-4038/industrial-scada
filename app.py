import streamlit as st
import datetime
import requests
import pandas as pd

st.set_page_config(page_title="Industrial MES & Task Time Tracker", layout="wide")

# Active Apps Script Web App URL
WEB_APP_URL = "https://script.google.com/macros/s/AKfycbzJAe0UgQO6YALceN2CgpsCGgnhF5zCe0_u6vLTyCEQmJNu1kRKpMbAWA8n-w86p4o/exec"

# Dark Industrial Theme Styling
st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #070b19 0%, #0f172a 50%, #081026 100%); color: #ffffff; }
    .card { background: rgba(30, 41, 59, 0.85); border: 1px solid rgba(56, 189, 248, 0.3); border-radius: 12px; padding: 18px; margin-bottom: 15px; }
    .green-tag { background: rgba(0, 230, 118, 0.2); color: #00e676; border: 1px solid #00e676; padding: 4px 12px; border-radius: 6px; font-weight: bold; }
    .yellow-tag { background: rgba(255, 235, 59, 0.2); color: #ffeb3b; border: 1px solid #ffeb3b; padding: 4px 12px; border-radius: 6px; font-weight: bold; }
    .orange-tag { background: rgba(255, 152, 0, 0.2); color: #ff9800; border: 1px solid #ff9800; padding: 4px 12px; border-radius: 6px; font-weight: bold; }
    .status-pill { padding: 4px 12px; border-radius: 12px; font-weight: bold; font-size: 13px; background: #0284c7; color: white; }
</style>
""", unsafe_allow_html=True)

# Factory Lines List
FACTORY_LINES = [
    "Liquid Manufacturing", 
    "Liquid Line 1", 
    "Liquid Line 2", 
    "Liquid Line 3", 
    "Powder Filling", 
    "Cream", 
    "Skyline", 
    "Softgel"
]

if 'tasks_db' not in st.session_state:
    st.session_state.tasks_db = [
        {
            "id": 101, 
            "task": "Batch Mixing & Reaction", 
            "line": "Liquid Manufacturing", 
            "priority": "🟠 High (Orange)", 
            "batch": "B-1001", 
            "next_batch_name": "PENTAVITE", 
            "next_batch_no": "123977", 
            "assigned_to": "EMP-101", 
            "status": "Running", 
            "start_time": "10:15:00", 
            "duration": "Active",
            "units_done": 1200,
            "units_left": 3800
        }
    ]

st.markdown("<h2 style='text-align: center; color: #38bdf8;'>🏭 Manufacturing Execution Dashboard</h2>", unsafe_allow_html=True)

tab_mgmt, tab_op = st.tabs(["👨‍💼 Management Portal (Assign & Track)", "👷 Operator Workstation (Status Buttons & Timers)"])

# =========================================================
# TAB 1: MANAGEMENT PORTAL
# =========================================================
with tab_mgmt:
    st.markdown("### 📋 Create & Assign Task with Priority Color")
    
    with st.form("create_task_form"):
        c1, c2, c3 = st.columns([3, 2, 2])
        task_name = c1.text_input("Task Description")
        line_name = c2.selectbox("Select Line", FACTORY_LINES)
        priority_color = c3.selectbox("Priority Color", ["🟢 Normal (Green)", "🟡 Medium (Yellow)", "🟠 High (Orange)"])
        
        c4, c5, c6 = st.columns([2, 2, 2])
        batch_no = c4.text_input("Current Batch No", value="B-2001")
        next_b_name = c5.text_input("Next Batch Name", value="PENTAVITE")
        next_b_no = c6.text_input("Next Batch No", value="123977")
        
        submitted = st.form_submit_button("🚀 Assign Task to Factory Floor", use_container_width=True)
        if submitted and task_name:
            new_id = len(st.session_state.tasks_db) + 101
            st.session_state.tasks_db.append({
                "id": new_id, 
                "task": task_name, 
                "line": line_name, 
                "priority": priority_color,
                "batch": batch_no, 
                "next_batch_name": next_b_name, 
                "next_batch_no": next_b_no, 
                "assigned_to": "Unassigned", 
                "status": "Pending",
                "start_time": "-", 
                "duration": "-",
                "units_done": 0,
                "units_left": 5000
            })
            st.success("Task created and broadcasted to Operator Workstation!")
            st.rerun()

    st.markdown("---")
    st.markdown("### 📊 Active Factory Tasks & Operator Status")
    
    df = pd.DataFrame(st.session_state.tasks_db)
    
    def color_priority(val):
        if "Orange" in str(val): return 'background-color: rgba(255, 152, 0, 0.25); color: #ff9800; font-weight: bold;'
        elif "Yellow" in str(val): return 'background-color: rgba(255, 235, 59, 0.25); color: #ffeb3b; font-weight: bold;'
        elif "Green" in str(val): return 'background-color: rgba(0, 230, 118, 0.25); color: #00e676; font-weight: bold;'
        return ''

    st.dataframe(df.style.map(color_priority, subset=['priority']), use_container_width=True)

# =========================================================
# TAB 2: OPERATOR WORKSTATION
# =========================================================
with tab_op:
    st.markdown("### ⏱️ Operator Status Action Buttons & Time Tracker")
    
    op_badge = st.text_input("🔑 Enter Your Operator Badge ID:", value="EMP-101")
    
    if not op_badge:
        st.warning("Please enter your Badge ID to work on tasks.")
    else:
        for item in st.session_state.tasks_db:
            p_class = "green-tag"
            if "Yellow" in item["priority"]: p_class = "yellow-tag"
            elif "Orange" in item["priority"]: p_class = "orange-tag"

            st.markdown(f"""
            <div class="card">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <h4 style="margin:0; color:#38bdf8;">Task #{item['id']}: {item['task']} ({item['line']})</h4>
                    <div>
                        <span class="{p_class}">Priority: {item['priority']}</span>
                        <span class="status-pill">Status: {item['status']}</span>
                    </div>
                </div>
                <p style="margin-top:8px; color:#cbd5e1; font-size:14px;">
                    <b>Batch:</b> {item['batch']} | <b>Next Batch:</b> {item['next_batch_name']} ({item['next_batch_no']}) | 👤 <b>Operator:</b> <span style="color:#38bdf8; font-weight:bold;">{item['assigned_to']}</span> | 
                    ⏱️ <b>Start:</b> {item['start_time']} | ⌛ <b>Duration:</b> {item['duration']}
                </p>
            </div>
            """, unsafe_allow_html=True)

            def update_status(new_status):
                now = datetime.datetime.now()
                now_str = now.strftime("%H:%M:%S")
                
                if item['start_time'] == "-":
                    item['start_time'] = now_str

                try:
                    start_dt = datetime.datetime.strptime(item['start_time'], "%H:%M:%S").replace(year=now.year, month=now.month, day=now.day)
                    duration_mins = round((now - start_dt).total_seconds() / 60, 1)
                    dur_str = f"{duration_mins} mins"
                except:
                    dur_str = "Active"

                item['status'] = new_status
                item['assigned_to'] = op_badge
                item['duration'] = dur_str

                # Payload aligned to Google Sheet Columns A to L
                payload = {
                    "timestamp": now_str,
                    "line": item['line'],
                    "task": item['task'],
                    "batch": item['batch'],
                    "next_batch_name": item['next_batch_name'],
                    "next_batch_no": item['next_batch_no'],
                    "status": new_status,
                    "units_done": item['units_done'],
                    "units_left": item['units_left'],
                    "badge_no": op_badge,
                    "priority": item['priority'],
                    "duration": dur_str
                }
                try: 
                    requests.post(WEB_APP_URL, json=payload, timeout=3)
                except: 
                    pass
                st.rerun()

            # Multiple Action Buttons Array
            b1, b2, b3, b4, b5, b6, b7 = st.columns(7)
            
            if b1.button("🚀 STARTUP", key=f"su_{item['id']}", use_container_width=True): update_status("Startup")
            if b2.button("▶️ RUNNING", key=f"rn_{item['id']}", use_container_width=True): update_status("Running")
            if b3.button("🔄 CHANGEOVER", key=f"co_{item['id']}", use_container_width=True): update_status("Changeover")
            if b4.button("⚠️ DOWNTIME", key=f"dt_{item['id']}", use_container_width=True): update_status("Downtime")
            if b5.button("☕ BREAK", key=f"br_{item['id']}", use_container_width=True): update_status("Break")
            if b6.button("🛠️ MAINT.", key=f"mt_{item['id']}", use_container_width=True): update_status("Maintenance")
            if b7.button("🛑 FINISH", key=f"fn_{item['id']}", use_container_width=True): update_status("Completed")

            st.markdown("<hr style='border-color: rgba(255,255,255,0.05);'>", unsafe_allow_html=True)
