import streamlit as st
import plotly.graph_objects as go # For the Donut Charts
from helper.logic import calculate_completion_percentage, get_time_difference, generate_suggestion # NEW IMPORT

userId = 'user1'
# def display_time_analyser():

#     st.divider()

#     # Layout: Split into two main sections (Left for Insights, Right for Charts)
#     col_left, col_right = st.columns([1, 1.2], gap="large")
def display_time_analyser():
    # --- MOCK DATA (This will eventually come from Andrea/Ikechukwu modules) ---
    tasks_done = 15
    tasks_total = 20
    screen_today = 3
    screen_yesterday = 1
    hw_today = 4
    # --- USING THE LOGIC ---
    completion_pct = calculate_completion_percentage(tasks_done, tasks_total)
    screen_diff = get_time_difference(screen_today, screen_yesterday)
    advice = generate_suggestion(screen_today, hw_today)

    st.divider()
    col_left, col_right = st.columns([1, 1.2], gap="large")
    # --- LEFT SECTION: Insights & AI Suggestions ---

    with col_left:
        with st.container(border=True):
            st.subheader("Daily Insight")
            # Using the calculated delta here
            st.info(f"⚠️ You spent **{screen_diff}hrs more** on Screen time than yesterday")
        
        st.markdown("### Suggestions for you [AI]")
        with st.expander("View Recommendations", expanded=True):
            st.write(advice) # Using the logic function output
            st.write("📚 Try to allocate an hour to study. Maybe a **50/10 study cycle**.")
            
    # --- RIGHT SECTION: The Visuals (Donut Charts) ---
    with col_right:
        st.subheader("Day's Date: Feb 23, 2026")
        
        # 1. Task Completion Donut (15/20 = 75%)
        fig_tasks = go.Figure(data=[go.Pie(
            labels=['Completed', 'Left'], 
            values=[tasks_done, tasks_total - tasks_done], 
            hole=.7,
            marker_colors=['#2ecc71', '#ecf0f1'],
            showlegend=False
        )])
        fig_tasks.update_layout(annotations=[dict(text=f'{completion_pct}%', x=0.5, y=0.5, font_size=20, showarrow=False)],
                                margin=dict(t=0, b=0, l=0, r=0), height=200)
        
        st.plotly_chart(fig_tasks, use_container_width=True)
        st.caption("✅ 15 Tasks Completed | ⭕ 5 Tasks Left")

        st.divider()

        # 2. Time Breakdown Metrics
        st.markdown("### Time Breakdown")
        m1, m2 = st.columns(2)
        with m1:
            st.metric("Homework", "4 hr")
            st.metric("Screentime", "3 hrs", delta="2 hrs", delta_color="inverse")
        with m2:
            st.metric("Chores", "1 hr")
            st.metric("Other", "1 hr 30m")

        st.success("✨ **Total Time Tracked: 9hr 45m**")

def display_app_page():
    """Remi's Module: The Time Analyser Page"""
    #st.header("📊 Time Analyser")
    #st.write(f"Logged in as: **{userId}**")
    # st.divider()
    # """Displays the home page of the app."""
    st.title('📊 Time Analyser')
    
    name = st.text_input('Enter your name')
    if name:
        st.write(f"Logged in as: **{name}**")
    
    st.divider()
    
    # Trigger your specific module
    display_time_analyser()


# This is the starting point for your app. You do not need to change these lines
if __name__ == '__main__':
    display_app_page()
