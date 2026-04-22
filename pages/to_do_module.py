def display_todo_page():
    """displays the todo list page of the app."""
    import streamlit as st
    from google.cloud import bigquery
    import time
    import vertexai
    from vertexai.generative_models import GenerativeModel
    from pages.home import display_home_page
    
    #go back button 
    header_col1, header_col2 = st.columns([4, 1])
    with header_col1:
        st.title("to-do")
    with header_col2:
        st.write("")
        if st.button("go back", type="primary"):
            st.session_state["nav_target"] = "home" #written by gemini
            st.rerun() #written by gemini
     
    client = None
    try:
        client = bigquery.Client(project="andrea-vazquez-nmsu")
        query = "SELECT * FROM `joshua-stevenson-hu.team_purple_dataset.tasks_table` WHERE username = @username"
        
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("username", "STRING", st.session_state.current_user["username"]),
            ]
        )
        tasks_list = client.query(query, job_config=job_config).to_dataframe().to_dict('records')

    except Exception as e:
        tasks_list = []
        st.error(f"could not get tasks, details:{e}")

    #write task
    st.subheader("add a new task!")
    new_task = st.text_input("task title...")
    #add task desc
    new_description = st.text_area("task description...", height=100)
    input_col1, input_col2 = st.columns(2)

    with input_col1:
        new_category = st.selectbox("category", ["school", "work", "life", "urgent 🕒"])
    with input_col2:
        new_date = st.date_input("date")

    # button to add task
    if st.button("add task"):
        if new_task: 
            unique_id = int(time.time()) 
            current_username = st.session_state.current_user["username"]
            
            insert_query = f"""
                INSERT INTO `joshua-stevenson-hu.team_purple_dataset.tasks_table` 
                (name_of_task, description, task_id, category, start_date, due_date, completion, username)
                VALUES 
                ('{new_task}', '{new_description}', {unique_id}, '{new_category}', '{new_date}', '{new_date}', False, '{current_username}')
            """
            try:
                client.query(insert_query).result()
                st.success("task added!")
                st.rerun()
            except Exception as e:
                st.error(f"failed to add task: {e}")

    st.divider()

    st.subheader("AI tasks overview")
    #description of the AI overview
    st.write("create an ai overview of your current to-dos to figure out what to do first!! ")
    if st.button("generate overview"):
        if not tasks_list:
            st.info("you don't have any tasks yet! add some so i can help you plan!")
        else:
            with st.spinner("analyzing tasks..."):
                try:
                    #tasks for ai
                    task_strings = []
                    for t in tasks_list:
                        desc = t.get('description', 'no description')
                        task_strings.append(f"- {t['name_of_task']} ({desc}) (Category: {t['category']}, Due: {t['due_date']})")
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
                    vertexai.init(project="andrea-vazquez-nmsu")
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
