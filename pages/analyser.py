#############################################################################
# pages/analyser.py
#
# This file contains the Time Analyser page of the app.
#############################################################################

import streamlit as st
import plotly.graph_objects as go
from datetime import date
from data_fetcher import get_user_activities, get_daily_summary, get_genai_advice, add_activity
from helper.logic import calculate_completion_percentage

USER_ID = 'user1'


@st.dialog("Add Activity")
def add_activity_dialog():
    """Popup for manually logging a new activity."""
    st.markdown("### Log a New Activity")

    title = st.text_input("Activity Title", placeholder="e.g. Scrolling TikTok")
    time_span = st.number_input("Time Spent (minutes)", min_value=1, max_value=600, value=30)
    category = st.selectbox("Category", ["Productive", "Unproductive", "Fun"])
    activity_date = st.date_input("Date", value=date.today())

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Save", type="primary", key="save_activity"):
            if not title:
                st.error("Please enter an activity title.")
            else:
                success, message = add_activity(USER_ID, title, time_span, category, activity_date)
                if success:
                    st.toast("Activity logged! 🎉")
                    st.rerun()
                else:
                    st.error(message)
    with col2:
        if st.button("Cancel", key="cancel_activity"):
            st.rerun()


@st.dialog("Day Breakdown")
def breakdown_dialog(activities):
    """Popup showing detailed breakdown of activities for a selected day."""
    st.markdown("### Activity Breakdown")
    if not activities:
        st.info("No activities logged for this day.")
        return

    for act in activities:
        st.markdown(f"**{act['title']}** — {act['time_span']} mins")
        st.caption(f"Category: {act['category']}")
        st.divider()


def display_time_analyser():
    today = str(date.today())

    # --- Fetch real data from BigQuery ---
    activities_today = get_user_activities(USER_ID, today)
    daily_summary = get_daily_summary(USER_ID, today)

    # --- Compute totals from real data ---
    total_minutes = sum(a['time_span'] for a in activities_today)
    productive_mins = sum(r['total_minutes'] for r in daily_summary if r['category'] == 'Productive')
    unproductive_mins = sum(r['total_minutes'] for r in daily_summary if r['category'] == 'Unproductive')
    fun_mins = sum(r['total_minutes'] for r in daily_summary if r['category'] == 'Fun')

    # --- TASK COMPLETION (mock data — replace with tasks_table query when ready) ---
    tasks_done = 15
    tasks_total = 20
    completion_pct = calculate_completion_percentage(tasks_done, tasks_total)

    st.divider()
    col_left, col_right = st.columns([1, 1.2], gap="large")

    # --- LEFT: Insights & AI Suggestions ---
    with col_left:
        with st.container(border=True):
            st.subheader("Daily Insight")
            if total_minutes == 0:
                st.info("No activities logged today yet.")
            else:
                st.info(f"⚠️ You've logged **{total_minutes:.0f} mins** of activity today.")

        st.markdown("### 🤖 AI Suggestions")
        with st.expander("View Recommendations", expanded=True):
            with st.spinner("Generating personalised advice..."):
                advice = get_genai_advice(USER_ID)
            st.write(advice['content'])

        st.markdown("---")
        if st.button("➕ Log Activity", key="log_activity"):
            add_activity_dialog()

        if st.button("📋 View Today's Breakdown", key="view_breakdown"):
            breakdown_dialog(activities_today)

    # --- RIGHT: Visuals ---
    with col_right:
        st.subheader(f"Today: {today}")

        # Task Completion Donut
        st.markdown("### ✅ Task Completion")
        fig_tasks = go.Figure(data=[go.Pie(
            labels=['Completed', 'Remaining'],
            values=[tasks_done, tasks_total - tasks_done],
            hole=.7,
            marker_colors=['#2ecc71', '#ecf0f1'],
            showlegend=False
        )])
        fig_tasks.update_layout(
            annotations=[dict(text=f'{completion_pct}%', x=0.5, y=0.5,
                              font_size=20, showarrow=False)],
            margin=dict(t=0, b=0, l=0, r=0), height=200
        )
        st.plotly_chart(fig_tasks, use_container_width=True)
        st.caption(f"✅ {tasks_done} Tasks Completed | ⭕ {tasks_total - tasks_done} Tasks Left")

        st.divider()

        # Time breakdown metrics
        st.markdown("### ⏱ Time Breakdown")
        m1, m2 = st.columns(2)
        with m1:
            st.metric("Productive", f"{productive_mins:.0f} mins")
            st.metric("Unproductive", f"{unproductive_mins:.0f} mins")
        with m2:
            st.metric("Fun", f"{fun_mins:.0f} mins")
            st.metric("Total Logged", f"{total_minutes:.0f} mins")

        if total_minutes > 0:
            st.success(f"✨ **Total Time Tracked: {total_minutes:.0f} mins**")
        else:
            st.warning("No activities logged today. Use '➕ Log Activity' to get started!")


def display_app_page():
    """Remi's Module: The Time Analyser Page"""
    st.title('📊 Time Analyser')

    name = st.text_input('Enter your name')
    if name:
        st.write(f"Logged in as: **{name}**")

    st.divider()
    display_time_analyser()


if __name__ == '__main__':
    display_app_page()