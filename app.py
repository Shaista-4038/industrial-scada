import streamlit as st
import datetime
import requests
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Industrial MES & Task Time Tracker", layout="wide")

WEB_APP_URL = "https://script.google.com/macros/s/AKfycbzJAe0UgQO6YALceN2CgpsCGgnhF5zCe0_u6vLTyCEQmJNu1kRKpMbAWA8n-w86p4o/exec"

# UI Styling
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

# State Management Initialization
if 'tasks_db' not in st.session_state:
    st.session_state.tasks_db = [
        {"id": 101, "task": "Bottle Washing & Sterilization", "line": "Liquid Line 1", "priority": "🟠 High (Orange)", "assigned_to": "Operator 12", "status": "In Progress", "start_time": "10:15:00", "end_time": "-", "duration": "Active"},
        {"id": 102, "task": "Syrup Blending & Filtering", "line": "Liquid Line 2", "priority": "🟡 Medium (Yellow)", "assigned_to": "Unassigned", "status": "Pending", "start_time": "-", "end_time": "-", "duration": "-"},
        {"id": 103, "task": "Cap Sealing & Inspection", "line": "Powder Filling", "priority": "🟢 Normal (Green)", "assigned_to": "Operator 05", "status": "Completed", "start_time": "08:30:00", "end_time": "09:45:00", "duration": "75.0 mins"}
    ]

st.markdown("<h2 style='text-align: center; color: #38bdf8;'>🏭 Industrial Task Time Tracker & MES Dashboard</h2>", unsafe_allow_html=True)

# Two Distinct Views
tab_mgmt, tab_op = st.tabs(["👨‍💼 Management Portal (Assign & Track)", "👷 Operator Workstation (Self-Pick & Timers)"])

# ---------------------------------------------------------
# TAB 1: MANAGEMENT PORTAL
# ---------------------------------------------------------
with tab_mgmt:
    st.markdown("### 📋 Create & Assign Task")
    with st.form("new_task_form"):
        c1, c2, c3, c4 = st.columns([3, 2, 2, 2])
        t_name = c1.text_input("Task Title")
        t_line = c2.selectbox("Production Line", ["Liquid Line 1", "Liquid Line 2", "Liquid Line 3", "Powder Filling", "Cream", "Skyline", "Softgel"])
        t_priority = c3.selectbox("Priority Color", ["🟢 Normal (Green)", "🟡 Medium (Yellow)", "🟠 High (Orange)"])
        t_assignee = c4.text_input("Assign Operator Badge (Optional)", placeholder="Leave empty for Open Pool")
        
        submit_task = st.form_submit_button("🚀 Create Task", use_container_width=True)
        if submit_task and t_name:
            new_id = len(st.session_state.tasks_db) + 101
            st.session_state.tasks_db.append({
                "id": new_id, "task": t_name, "line": t_line, "priority": t_priority,
                "assigned_to": t_assignee if t_assignee else "Unassigned",
                "status": "Pending", "start_time": "-", "end_time": "-", "duration": "-"
            })
            st.success("Task Created and Broadcasted to Operator Portal!")
            st.rerun()

    st.markdown("---")
    st.markdown("### 📊 Live Task Progress & Time Analytics")
    
    df = pd.DataFrame(st.session_state.tasks_db)
    
    # Priority Color Highlights in Management Table
    def highlight_priority(val):
        if "Orange" in str(val): return 'background-color: rgba(255, 152, 0, 0.25); color: #ff9800; font-weight: bold;'
        elif "Yellow" in str(val): return 'background-color: rgba(255, 235, 59, 0.25); color: #ffeb3b; font-weight: bold;'
        elif "Green" in str(val): return 'background-color: rgba(0, 230, 118, 0.25); color: #00e676; font-weight: bold;'
        return ''

    st.dataframe(df.style.map(highlight_priority, subset=['priority']), use_container_width=True)

# ---------------------------------------------------------
# TAB 2: OPERATOR WORKSTATION
# ---------------------------------------------------------
with tab_op:
    st.markdown("### ⏱️ Active Tasks & Timer Panel")
    
    op_badge = st.text_input("🔑 Enter Your Operator Badge ID:", value="Operator 12")
    
    if not op_badge:
        st.warning("Please enter your Badge ID to access or pick tasks.")
    else:
        for item in st.session_state.tasks_db:
            # Color Styling based on Priority
            p_cls = "green-tag"
            if "Yellow" in item["priority"]: p_cls = "yellow-tag"
            elif "Orange" in item["priority"]: p_cls = "orange-tag"

            status_badge = f"<span class='badge badge-unassigned'>{item['status']}</span>"
            if item['status'] == 'In Progress': status_badge = "<span class='badge badge-started'>IN PROGRESS</span>"
            elif item['status'] == 'Completed': status_badge = "<span class='badge badge-completed'>COMPLETED</span>"

            st.markdown(f"""
            <div class="card">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <h4 style="margin:0; color:#38bdf8;">#{item['id']} - {item['task']} ({item['line']})</h4>
                    <div>
                        <span class="{p_cls}">{item['priority']}</span>
                        {status_badge}
                    </div>
                </div>
                <p style="margin-top:8px; margin-bottom:4px; color:#cbd5e1; font-size:14px;">
                    👤 <b>Assigned To:</b> {item['assigned_to']} | ⏱️ <b>Start Time:</b> {item['start_time']} | 🏁 <b>End Time:</b> {item['end_time']} | ⌛ <b>Duration:</b> {item['duration']}
                </p>
            </div>
            """, unsafe_allow_html=True)

            c_btn1, c_btn2, _ = st.columns([2, 2, 6])
            
            # Action Buttons
            if item['status'] == 'Pending':
                if c_btn1.button(f"▶️ Pick & START Task #{item['id']}", key=f"start_{item['id']}"):
                    now_str = datetime.datetime.now().strftime("%H:%M:%S")
                    item['status'] = "In Progress"
                    item['assigned_to'] = op_badge
                    item['start_time'] = now_str
                    item['duration'] = "Active"
                    
                    # Push to Database (Google Sheets)
                    payload = {"line": item['line'], "task": item['task'], "priority": item['priority'], "status": "In Progress", "badge_no": op_badge, "timestamp": now_str, "duration": "Started"}
                    try: requests.post(WEB_APP_URL, json=payload, timeout=3)
                    except: pass
                    st.rerun()

            elif item['status'] == 'In Progress' and item['assigned_to'] == op_badge:
                if c_btn2.button(f"⏹️ FINISH Task #{item['id']}", key=f"finish_{item['id']}"):
                    now = datetime.datetime.now()
                    now_str = now.strftime("%H:%M:%S")
                    
                    # Calculate exact elapsed duration
                    try:
                        start_dt = datetime.datetime.strptime(item['start_time'], "%H:%M:%S").replace(year=now.year, month=now.month, day=now.day)
                        duration_mins = round((now - start_dt).total_seconds() / 60, 1)
                        dur_str = f"{duration_mins} mins"
                    except:
                        dur_str = "Completed"

                    item['status'] = "Completed"
                    item['end_time'] = now_str
                    item['duration'] = dur_str

                    # Push Final Duration to Database (Google Sheets)
                    payload = {"line": item['line'], "task": item['task'], "priority": item['priority'], "status": "Completed", "badge_no": op_badge, "timestamp": now_str, "duration": dur_str}
                    try: requests.post(WEB_APP_URL, json=payload, timeout=3)
                    except: pass
                    st.rerun()
            
            st.markdown("<hr style='border-color: rgba(255,255,255,0.05); margin: 5px 0;'>", unsafe_allow_html=True)
