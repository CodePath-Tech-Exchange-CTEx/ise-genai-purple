from google.cloud import bigquery
# table `joshua-stevenson-hu.team_purple_dataset.`
client = bigquery.Client()



def add_notification():
    pass



def get_item_data(i_title, i_type):

    if not i_type or not i_title:
        return None

    if i_type.startswith("Event"):
        event = {}
        query = """
        SELECT title, start_date_time
        FROM `joshua-stevenson-hu.team_purple_dataset.events_table`
        WHERE LOWER(title) = LOWER(@title)
        LIMIT 1
        """

        job_config = bigquery.QueryJobConfig(query_parameters=[bigquery.ScalarQueryParameter("title", "STRING", i_title)])

        results = client.query(query, job_config=job_config).result()
        if results.total_rows == 0:
            return None
        else:
            row = next(results)

        event["title"] = row.title
        event["date"] = row.start_date_time
        return events
    elif i_type.startswith("Task"):
        task = {}
        query = """
        SELECT name_of_task, due_date
        FROM `joshua-stevenson-hu.team_purple_dataset.tasks_table`
        WHERE LOWER(name_of_task) = LOWER(@title)
        LIMIT 1
        """

        job_config = bigquery.QueryJobConfig(query_parameters[bigquery.ScalarQueryParameter("title", "STRING", i_title)])

        results = client.query(query, job_config=job_config).result()
        if results.total_rows == 0:
            return None
        else:
            row = next(results)
        
        task["title"] = row.name_of_task
        task["date"] = row.due_date
        return task
    else:
        return None

