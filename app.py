import streamlit as st
import datetime
import requests
import pandas as pd

st.set_page_config(page_title="Industrial MES & Task Time Tracker", layout="wide")

# Active Apps Script Web App URL
WEB_APP_URL = "https://script.google.com/macros/s/AKfycbzJAe0UgQO6YALceN2CgpsCGgnhF5zCe0_u6vLTyCEQmJNu1kRKpMbAWA8n-w86p4o/exec"

# Dark Industrial UI Styling
st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #070b19 0%, #0f172a 50%, #081026 100%); color: #ffffff; }
    .card { background: rgba(30, 41, 59, 0.85); border: 1px solid rgba(56, 189, 248, 0.3); border-radius: 12px; padding: 18px; margin-bottom: 15px; }
    .green-tag { background: rgba(0, 230, 118, 0.2); color: #00e676; border: 1px solid #00e676; padding: 4px 12px; border-radius: 6px; font-weight: bold; }
    .yellow-tag { background: rgba(255, 235, 59, 0.2); color: #ffeb3b; border: 1px solid #ffeb3b; padding: 4px 12px; border-radius: 6px; font-weight: bold; }
    .orange-tag { background: rgba(255, 152, 0, 0.2); color: #ff9800; border: 1px solid #ff9800; padding: 4px 12px; border-radius: 6px; font-weight: bold; }
    .badge { padding: 4px 10px; border-radius: 12px; font-weight: bold; font-size: 12px; }
    .badge-started { background: #0284c7; color: white; }
    .badge-completed { background: #16a34a; color: white; }
    .badge-unassigned { background: #475569; color: white; }
</style>
""", unsafe_allow_html=True)

# Shared In-Memory State for Live Dashboard Synchronization
if 'tasks_db' not in st.session_state:
    st.session_state.tasks_db = [
        {
            "id": 101, 
            "task": "Bottle Washing & Sterilization", 
            "line": "Liquid Line 1", 
            "priority": "🟠 High (Orange)", 
            "batch": "B-1001", 
            "next_batch_name": "PENTAVITE", 
            "next_batch_no": "123977", 
            "assigned_to": "EMP-101", 
            "status": "In Progress", 
            "start_time": "10:15:00", 
            "end_time": "-", 
            "duration": "Active",
            "units_done": 1200,
            "units_left": 3800
        },
        {
            "id": 102, 
            "task": "Syrup Blending & Filtering", 
            "line": "Liquid Line 2", 
            "priority": "🟡 Medium (Yellow)", 
            "batch": "B-1002", 
            "next_batch_name": "SAMBUCOL", 
            "next_batch_no": "145730", 
            "assigned_to": "Unassigned", 
            "status": "Pending", 
            "start_time": "-", 
            "end_time": "-", 
            "duration": "-",
            "units_done": 0,
            "units_left": 5000
        }
    ]

st.markdown("<h2 style='text-align: center; color: #38bdf8;'>🏭 Manufacturing Execution Dashboard</h2>", unsafe_allow_html=True)

# Two Portals via Tabs
tab_mgmt, tab_op = st.tabs(["👨‍💼 Management Portal (Assign & Track)", "👷 Operator Workstation (Self-Pick & Timers)"])

# =========================================================
# TAB 1: MANAGEMENT PORTAL
# =========================================================
with tab_mgmt:
    st.markdown("### 📋 Create & Assign Task with Priority Color")
    
    with st.form("create_task_form"):
        c1, c2, c3 = st.columns([3, 2, 2])
        task_name = c1.text_input("Task Description")
        line_name = c2.selectbox("Select Line", ["Liquid Line 1", "Liquid Line 2", "Liquid Line 3", "Powder Filling", "Cream", "Skyline", "Softgel"])
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
                "end_time": "-", 
                "duration": "-",
                "units_done": 0,
                "units_left": 5000
            })
            st.success("Task assigned successfully and visible on Operator Workstation!")
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
    st.markdown("### ⏱️ Operator Self-Assignment & Live Time Tracker")
    
    op_badge = st.text_input("🔑 Enter Your Operator Badge ID:", value="EMP-101")
    
    if not op_badge:
        st.warning("Please enter your Badge ID to work on tasks.")
    else:
        for item in st.session_state.tasks_db:
            p_class = "green-tag"
            if "Yellow" in item["priority"]: p_class = "yellow-tag"
            elif "Orange" in item["priority"]: p_class = "orange-tag"

            status_badge = f"<span class='badge badge-unassigned'>{item['status']}</span>"
            if item['status'] == 'In Progress': status_badge = "<span class='badge badge-started'>IN PROGRESS</span>"
            elif item['status'] == 'Completed': status_badge = "<span class='badge badge-completed'>COMPLETED</span>"

            st.markdown(f"""
            <div class="card">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <h4 style="margin:0; color:#38bdf8;">Task #{item['id']}: {item['task']} ({item['line']})</h4>
                    <div>
                        <span class="{p_class}">Priority: {item['priority']}</span>
                        {status_badge}
                    </div>
                </div>
                <p style="margin-top:8px; color:#cbd5e1; font-size:14px;">
                    <b>Batch:</b> {item['batch']} | <b>Next Batch:</b> {item['next_batch_name']} ({item['next_batch_no']}) | 👤 <b>Assigned To:</b> <span style="color:#38bdf8; font-weight:bold;">{item['assigned_to']}</span> | 
                    ⏱️ <b>Start:</b> {item['start_time']} | ⌛ <b>Duration:</b> {item['duration']}
                </p>
            </div>
            """, unsafe_allow_html=True)

            b1, b2, _ = st.columns([2, 2, 6])

            # Button 1: START / Self-Pick
            if item['status'] == 'Pending':
                if b1.button(f"▶️ Pick & START Task #{item['id']}", key=f"start_{item['id']}"):
                    now_str = datetime.datetime.now().strftime("%H:%M:%S")
                    item['status'] = "In Progress"
                    item['assigned_to'] = op_badge
                    item['start_time'] = now_str
                    item['duration'] = "Active"

                    # Payload specifically matching Google Sheet Columns A to L
                    payload = {
                        "timestamp": now_str,          # Col A
                        "line": item['line'],           # Col B
                        "task": item['task'],           # Col C
                        "batch": item['batch'],         # Col D
                        "next_batch_name": item['next_batch_name'], # Col E
                        "next_batch_no": item['next_batch_no'],     # Col F
                        "status": "In Progress",        # Col G
                        "units_done": item['units_done'], # Col H
                        "units_left": item['units_left'], # Col I
                        "badge_no": op_badge,           # Col J
                        "priority": item['priority'],   # Col K
                        "duration": "Started"           # Col L
                    }
                    try: requests.post(WEB_APP_URL, json=payload, timeout=3)
                    except: pass
                    st.rerun()

            # Button 2: FINISH Task & Log Duration
            elif item['status'] == 'In Progress' and item['assigned_to'] == op_badge:
                if b2.button(f"⏹️ FINISH Task #{item['id']}", key=f"finish_{item['id']}"):
                    now = datetime.datetime.now()
                    now_str = now.strftime("%H:%M:%S")
                    
                    # Calculate exact task duration
                    try:
                        start_dt = datetime.datetime.strptime(item['start_time'], "%H:%M:%S").replace(year=now.year, month=now.month, day=now.day)
                        duration_mins = round((now - start_dt).total_seconds() / 60, 1)
                        dur_str = f"{duration_mins} mins"
                    except:
                        dur_str = "Completed"

                    item['status'] = "Completed"
                    item['end_time'] = now_str
                    item['duration'] = dur_str
                    item['units_done'] = 5000
                    item['units_left'] = 0

                    # Payload specifically matching Google Sheet Columns A to L
                    payload = {
                        "timestamp": now_str,          # Col A
                        "line": item['line'],           # Col B
                        "task": item['task'],           # Col C
                        "batch": item['batch'],         # Col D
                        "next_batch_name": item['next_batch_name'], # Col E
                        "next_batch_no": item['next_batch_no'],     # Col F
                        "status": "Completed",          # Col G
                        "units_done": 5000,             # Col H
                        "units_left": 0,                # Col I
                        "badge_no": op_badge,           # Col J
                        "priority": item['priority'],   # Col K
                        "duration": dur_str             # Col L
                    }
                    try: requests.post(WEB_APP_URL, json=payload, timeout=3)
                    except: pass
                    st.rerun()

            st.markdown("<hr style='border-color: rgba(255,255,255,0.05);'>", unsafe_allow_html=True)
