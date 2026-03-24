def display_todo_page():
    """displays the todo list page of the app."""
    import streamlit as st
    from google.cloud import bigquery
    import time
    st.title("to-do")
    client = bigquery.Client()
    query = "SELECT * FROM `joshua-stevenson-hu.team_purple_dataset.tasks_table`"
    try:
        tasks_list = client.query(query).to_dataframe().to_dict('records')
    except Exception as e:
        tasks_list = []

    #write task
    st.subheader("add a new task!")
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
            unique_id = int(time.time()) 
            
            insert_query = f"""
                INSERT INTO `joshua-stevenson-hu.team_purple_dataset.tasks_table` 
                (name_of_task, task_id, category, start_date, due_date, completion)
                VALUES 
                ('{new_task}', {unique_id}, '{new_category}', '{new_date}', '{new_date}', False)
            """
            client.query(insert_query).result()
            
            st.success("task added!")
            st.rerun() 

    st.divider()
    col_school, col_work, col_life, col_urgent = st.columns(4)

    with col_school:
        st.subheader(":blue[SCHOOL]")
        for t in tasks_list:
            if t["category"] == "school":
                st.checkbox(f"{t['name_of_task']} ({t['due_date']})", key=str(t['task_id'])+'school')

    with col_work:
        st.subheader(":green[WORK]")
        for t in tasks_list:
            if t["category"] == "work":
                st.checkbox(f"{t['name_of_task']} ({t['due_date']})", key=str(t['task_id'])+'work')

    with col_life:
        st.subheader(":orange[LIFE]")
        for t in tasks_list:
            if t["category"] == "life":
                st.checkbox(f"{t['name_of_task']} ({t['due_date']})", key=str(t['task_id'])+'life')

    with col_urgent:
        st.subheader(":red[URGENT 🕒]")
        for t in tasks_list:
            if t["category"] == "urgent 🕒":
                st.checkbox(f"{t['name_of_task']} ({t['due_date']})", key=str(t['task_id'])+'urgent')
if __name__ == "__main__":
    display_todo_page()