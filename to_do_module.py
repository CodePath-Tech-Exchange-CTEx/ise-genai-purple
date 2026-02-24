#############################################################################
# app.py
#
# This file contains the entrypoint for the app.
#
#############################################################################

import streamlit as st
from modules import display_my_custom_component, display_post, display_genai_advice, display_activity_summary, display_recent_workouts
from data_fetcher import get_user_posts, get_genai_advice, get_user_profile, get_user_sensor_data, get_user_workouts

userId = 'user1'


def display_app_page():
    """Displays the home page of the app."""
    st.title('Welcome to SDS!')

    # An example of displaying a custom component called "my_custom_component"
    value = st.text_input('Enter your name')
    display_my_custom_component(value)


# This is the starting point for your app. You do not need to change these lines
def display_todo_page():
    """displays the todo list page of the app."""
    import streamlit as st
    st.title("to-do")

    #list to hold tasks
    if "tasks" not in st.session_state:
        st.session_state.tasks = []

    #write task
    st.write("###add a new task")
    input_col1, input_col2, input_col3 = st.columns([1, 1, 2])

    with input_col1:
        new_category = st.selectbox("category", ["school", "work", "life", "urgent 🕒"])
    with input_col2:
        new_date = st.date_input("date")
    with input_col3:
        new_task = st.text_input("new task......")

    # button to add task
    if st.button("add task"):
        if new_task: 
            st.session_state.tasks.append({
                "category": new_category, 
                "date": new_date, 
                "task": new_task
            })
            st.success("task added!")
            st.rerun() 

    st.divider()
    col_school, col_work, col_life, col_urgent = st.columns(4)

    with col_school:
        st.subheader("SCHOOL")
        for t in st.session_state.tasks:
            if t["category"] == "school":
                st.checkbox(f"{t['task']} ({t['date'].strftime('%m/%d')})", key=t['task']+'school')

    with col_work:
        st.subheader("WORK")
        for t in st.session_state.tasks:
            if t["category"] == "work":
                st.checkbox(f"{t['task']} ({t['date'].strftime('%m/%d')})", key=t['task']+'work')

    with col_life:
        st.subheader("LIFE")
        for t in st.session_state.tasks:
            if t["category"] == "life":
                st.checkbox(f"{t['task']} ({t['date'].strftime('%m/%d')})", key=t['task']+'life')

    with col_urgent:
        st.subheader("URGENT 🕒")
        for t in st.session_state.tasks:
            if t["category"] == "urgent 🕒":
                st.checkbox(f"{t['task']} ({t['date'].strftime('%m/%d')})", key=t['task']+'urgent')


# --- EXECUTION BLOCK ---
# We change this to run YOUR function so you can actually see the to-do list
if __name__ == '__main__':
    display_todo_page()