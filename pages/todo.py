def display_todo_page():
    """displays the todo list page of the app."""
    import streamlit as st
    from google.cloud import bigquery
    import time
    import vertexai
    from vertexai.generative_models import GenerativeModel
    
    st.title("to-do")
    client = None
    try:
        client = bigquery.Client(project="project-6e90bd07-d669-4de8-930")
        query = "SELECT * FROM `joshua-stevenson-hu.team_purple_dataset.tasks_table`"
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
            try:
                client.query(insert_query).result()
                st.success("task added!")
                st.rerun()
            except Exception as e:
                st.error(f"Failed to add task: {e}")

    st.divider()

    st.subheader("AI tasks overview")
    if st.button("generate overview"):
        if not tasks_list:
            st.info("you don't have any tasks yet! add some so i can help you plan!")
        else:
            with st.spinner("analyzing tasks..."):
                try:
                    #tasks for ai
                    task_strings = []
                    for t in tasks_list:
                        task_strings.append(f"- {t['name_of_task']} (Category: {t['category']}, Due: {t['due_date']})")
                    task_summary = "\n".join(task_strings)

                    #ai prompt
                    prompt = f"""
                    You are a helpful productivity coach for the user. 
                    Here is the current to-do list:
                    
                    {task_summary}

                    Please give me a short, fun overview of what needs to be prioritized first. 
                    Also provide quick tips to stay focused/productive. 
                    Keep the response short.
                    """
                    #vertexai
                    vertexai.init(project="project-6e90bd07-d669-4de8-930")
                    model = GenerativeModel("gemini-2.5-flash-lite")
                    response = model.generate_content(prompt)

                    #output response
                    st.info(response.text)
                except Exception as e:
                    st.error(f"couldn't generate the overview: {e}")               
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