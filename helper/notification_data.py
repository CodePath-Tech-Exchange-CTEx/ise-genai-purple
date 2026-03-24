from google.cloud import bigquery

# Initialize the BigQuery client
# Assumes GOOGLE_APPLICATION_CREDENTIALS environment variable is set locally
client = bigquery.Client()

def update_reminder(reminder, new_dt, new_repeated, new_interval):
    """
    Updates an existing notification record in BigQuery.
    Identifies the record by its title.
    """
    query = """
    UPDATE `joshua-stevenson-hu.team_purple_dataset.notification_table`
    SET date_time = @date_time,
        is_repeated = @is_repeated,
        repeat_interval = @repeat_interval
    WHERE title = @title
    """ 
    # Use ScalarQueryParameter to safely handle data types and prevent SQL injection
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("title", "STRING", reminder["title"]),
            bigquery.ScalarQueryParameter("date_time", "DATETIME", new_dt),
            bigquery.ScalarQueryParameter("is_repeated", "BOOL", new_repeated),
            bigquery.ScalarQueryParameter("repeat_interval", "INTEGER", new_interval),
        ]
    )

    # Execute the query and wait for the result to confirm completion
    client.query(query, job_config=job_config).result()

def delete_reminder(rtitle):
    """
    Removes a notification from the table based on the title.
    """
    query = """
    DELETE FROM `joshua-stevenson-hu.team_purple_dataset.notification_table`
    WHERE title = @title
    """

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("title", "STRING", rtitle),
        ]
    )

    client.query(query, job_config=job_config).result()

def add_notification(data):
    """
    Inserts a new reminder record into the notifications table.
    """
    query = """
    INSERT INTO `joshua-stevenson-hu.team_purple_dataset.notification_table`
    (title, type, date_time, is_repeated, repeat_interval)
    VALUES (@title, @type, @date_time, @is_repeated, @repeat_interval)
    """

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("title", "STRING", data["title"]),
            bigquery.ScalarQueryParameter("type", "STRING", data["type"]),
            bigquery.ScalarQueryParameter("date_time", "DATETIME", data["date_time"]),
            bigquery.ScalarQueryParameter("is_repeated", "BOOL", data["repeat"]),
            bigquery.ScalarQueryParameter("repeat_interval", "INTEGER", data["interval"]),
        ]
    )

    client.query(query, job_config=job_config).result()

def get_notifications():
    """
    Retrieves all active notifications.
    Returns a list of dictionaries for easy use in Streamlit UI.
    """
    query = """
    SELECT title, type, date_time, is_repeated, repeat_interval 
    FROM `joshua-stevenson-hu.team_purple_dataset.notification_table`
    """

    results = client.query(query).result()
    notifications = []
    
    # Map BigQuery Row objects to standard Python dictionaries
    for row in results:
        notifications.append({
            "title": row.title,
            "type": row.type,
            "date_time": row.date_time,
            "repeat": row.is_repeated,
            "interval": row.repeat_interval
        })
    return notifications

def get_item_data(i_title, i_type):
    """
    Validates if a title exists in the source Calendar or Task tables.
    If found, returns a formatted string containing the title and the scheduled date.
    Used for cross-referencing during 'Add Reminder'.
    """
    if not i_type or not i_title:
        return None

    # Logic for Calendar Events
    if i_type.startswith("Event"):
        query = """
        SELECT title, start_date_time
        FROM `joshua-stevenson-hu.team_purple_dataset.events_table`
        WHERE LOWER(title) = LOWER(@title)
        LIMIT 1
        """

        job_config = bigquery.QueryJobConfig(query_parameters=[
            bigquery.ScalarQueryParameter("title", "STRING", i_title)
        ])

        results = client.query(query, job_config=job_config).result()
        if results.total_rows == 0:
            return None
        
        row = next(results)
        # Format: "Meeting at 3/23 10:00am"
        return f"{row.title} at {row.start_date_time.strftime('%#m/%#d %#I:%M%p')}"

    # Logic for To-Do Tasks
    elif i_type.startswith("Task"):
        query = """
        SELECT name_of_task, due_date
        FROM `joshua-stevenson-hu.team_purple_dataset.tasks_table`
        WHERE LOWER(name_of_task) = LOWER(@title)
        LIMIT 1
        """

        job_config = bigquery.QueryJobConfig(query_parameters=[
            bigquery.ScalarQueryParameter("title", "STRING", i_title)
        ])

        results = client.query(query, job_config=job_config).result()
        if results.total_rows == 0:
            return None
        
        row = next(results)
        # Format: "Laundry due 3/23"
        return f"{row.name_of_task} due {row.due_date.strftime('%#m/%#d')}"

    return None