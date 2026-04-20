#############################################################################
# pages/home.py
#
# This file contains the Home page of the app — a summary overview.
#############################################################################

import streamlit as st
import plotly.graph_objects as go
from datetime import date
from data_fetcher import get_todays_tasks, get_upcoming_reminders, get_home_ai_overview, add_task
from helper.logic import calculate_completion_percentage

@st.dialog("Create a New Task! 📝")
def add_task_dialog(username):
    """Popup for creating a new task from the home page."""

    title = st.text_input("Task Title", placeholder="e.g. Finish assignment...")
    description = st.text_area("Task Description (optional)", placeholder="Add more details...")
    
    col_c, col_d = st.columns(2)
    with col_c:
        category = st.selectbox("Category", ["school", "work", "life", "urgent"])
    with col_d:
        due_date = st.date_input("Due Date (optional)", value=date.today())

    st.markdown("---")
    col_b1, col_b2 = st.columns(2)
    with col_b1:
        if st.button("✅ Create Task", type="primary", width='stretch'):
            if not title:
                st.error("Please enter a task title!")
            else:
                success, message = add_task(username, title, category, due_date)
                if success:
                    st.session_state.new_task_added = True
                    st.session_state.new_task_name = title
                    st.rerun()
                else:
                    st.error(message)
    with col_b2:
        if st.button("Close ✕", width='stretch'):
            st.rerun()

def display_home_page():
    """Displays the home page with a summary overview of the app."""

    # --- Get logged in user ---
    current_user = st.session_state.get("current_user", {})
    username = current_user.get("username", "User") if isinstance(current_user, dict) else current_user

    today = date.today() 
    formatted_date = today.strftime("%A, %B %d %Y")

    # Category color mapping
    CATEGORY_COLORS = {
        "school": "#1a73e8",
        "work":   "#2e7d32",
        "life":   "#e65100",
        "urgent": "#c62828",
    }

    # --- Fetch real data ---
    tasks = get_todays_tasks(username)
    reminders = get_upcoming_reminders(username, limit=3)

    # --- Compute task completion ---
    tasks_total = len(tasks)
    tasks_done = len([t for t in tasks if t['completion']])
    completion_pct = calculate_completion_percentage(tasks_done, tasks_total)

    # --- Header ---
    st.title(f"Welcome, {username}! 👋")
    st.subheader(f"Today is {formatted_date}")
    st.divider()

    if st.session_state.get("new_task_added"):
        st.toast(f"✅ '{st.session_state.new_task_name}' added to your tasks!")
        st.session_state.new_task_added = False
        st.session_state.new_task_name = None

    col_left, col_right = st.columns([1.2, 1], gap="large")

    # --- LEFT: AI Overview + Task List ---
    with col_left:

        # Today's Tasks
        st.markdown("### 📋 Today's Tasks")
        if not tasks:
            st.info("No tasks due today! Head to the Todo page to add some.")
        else:
            col_t1, col_t2 = st.columns(2)
            for i, task in enumerate(tasks):
                icon = "✅" if task['completion'] else "⭕"
                category = task.get('category', '').lower()
                color = CATEGORY_COLORS.get(category, "#888888")
                badge = f'<span style="background-color:{color}; color:white; padding:2px 8px; border-radius:12px; font-size:11px; margin-left:6px;">{category.upper()}</span>'
                task_html = f'{icon} {task["name_of_task"]} {badge}'
                if i % 2 == 0:
                    with col_t1:
                        st.markdown(task_html, unsafe_allow_html=True)
                else:
                    with col_t2:
                        st.markdown(task_html, unsafe_allow_html=True)

        st.markdown("---")

        # AI Overview Box
        st.markdown("### 🤖 AI Overview for Today")
        with st.container(border=True):
            try:
                with st.spinner("Generating your daily overview..."):
                    overview = get_home_ai_overview(username)
                    st.write(overview)
            except Exception as e:
                st.warning(f"⚠️ Error: {str(e)}")

    # --- RIGHT: Donut Chart + Buttons + Reminders ---
    with col_right:

        # Task Completion Donut
        st.markdown("### ✅ Task Completion")
        if tasks_total == 0:
            st.info("No tasks for today yet.")
        else:
            fig = go.Figure(data=[go.Pie(
                labels=['Completed', 'Remaining'],
                values=[tasks_done, tasks_total - tasks_done],
                hole=.7,
                marker_colors=['#2ecc71', '#ecf0f1'],
                showlegend=False
            )])
            fig.update_layout(
                annotations=[dict(text=f'{completion_pct}%', x=0.5, y=0.5,
                                  font_size=20, showarrow=False)],
                margin=dict(t=0, b=0, l=0, r=0), height=200
            )
            st.plotly_chart(fig, width='stretch')
            st.caption(f"✅ {tasks_done} Done | ⭕ {tasks_total - tasks_done} Remaining")

        # Buttons
        col_b1, col_b2 = st.columns(2)
        with col_b1:
            if st.button("➕ Add Task", width='stretch'):
                add_task_dialog(username)
        with col_b2:
            if st.button("📅 See Calendar", width='stretch'):
                st.info("Use the nav bar above!")

        # Upcoming Reminders
        st.markdown("### 🔔 Upcoming Reminders")
        if not reminders:
            st.info("No upcoming reminders.")
        else:
            for reminder in reminders:
                with st.container(border=True):
                    st.markdown(f"**{reminder['title']}**")
                    st.caption(f"🕐 {reminder['date_time']} · {reminder['type']}")


if __name__ == '__main__':
    display_home_page()