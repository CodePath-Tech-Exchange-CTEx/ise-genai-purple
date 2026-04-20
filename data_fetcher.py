#############################################################################
# data_fetcher.py
#
# This file contains functions to fetch data needed for the app.
#############################################################################

from google.cloud import bigquery
from datetime import date
import vertexai
from vertexai.generative_models import GenerativeModel

# --- Setup ---
def get_client():
    return bigquery.Client()
TABLE = "joshua-stevenson-hu.team_purple_dataset.analyser_table"
PROJECT_ID = "oluwaremilekun-adeshina-fisk"
REGION = "us-central1"

users = {
    'user1': {
        'full_name': 'Remi',
        'username': 'remi_the_rems',
        'date_of_birth': '1990-01-01',
        'profile_image': 'https://upload.wikimedia.org/wikipedia/commons/c/c8/Puma_shoes.jpg',
        'friends': ['user2', 'user3', 'user4'],
    },
    'user2': {
        'full_name': 'Blake',
        'username': 'blake',
        'date_of_birth': '1990-01-01',
        'profile_image': 'https://upload.wikimedia.org/wikipedia/commons/c/c8/Puma_shoes.jpg',
        'friends': ['user1'],
    },
    'user3': {
        'full_name': 'Jordan',
        'username': 'jordanjordanjordan',
        'date_of_birth': '1990-01-01',
        'profile_image': 'https://upload.wikimedia.org/wikipedia/commons/c/c8/Puma_shoes.jpg',
        'friends': ['user1', 'user4'],
    },
    'user4': {
        'full_name': 'Gemmy',
        'username': 'gems',
        'date_of_birth': '1990-01-01',
        'profile_image': 'https://upload.wikimedia.org/wikipedia/commons/c/c8/Puma_shoes.jpg',
        'friends': ['user1', 'user3'],
    },
}


def get_user_profile(user_id):
    """Returns information about the given user."""
    if user_id not in users:
        raise ValueError(f'User {user_id} not found.')
    return users[user_id]


def get_user_activities(user_id, date, username):
    """
    GET #1: Returns all activity entries for a specific user on a given date.
    e.g. get_user_activities('user1', '2026-02-23')
    """
    query = """
        SELECT title, time_span, category, date
        FROM `{table}`
        WHERE username = @username
          AND date = @date
        ORDER BY time_span DESC
    """.format(table=TABLE)

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("user_id", "STRING", user_id),
            bigquery.ScalarQueryParameter("date", "DATE", str(date)),
            bigquery.ScalarQueryParameter("username", "STRING", username),
        ]
    )

    results = get_client().query(query, job_config=job_config).result()
    return [dict(row) for row in results]


def get_activity_history(user_id, username, days=7):
    """
    GET #2: Returns all activities for a user over the last N days.
    e.g. get_activity_history('user1', days=7)
    """
    query = """
        SELECT title, time_span, category, date
        FROM `{table}`
        WHERE username = @username
          AND date >= DATE_SUB(CURRENT_DATE(), INTERVAL @days DAY)
        ORDER BY date DESC
    """.format(table=TABLE)

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("user_id", "STRING", user_id),
            bigquery.ScalarQueryParameter("days", "INT64", days),
            bigquery.ScalarQueryParameter("username", "STRING", username),
        ]
    )

    results = get_client().query(query, job_config=job_config).result()
    return [dict(row) for row in results]


def get_activities_by_category(user_id, category, username):
    """
    GET #3: Returns all activities for a user filtered by category.
    e.g. get_activities_by_category('user1', 'Productive')
    """
    query = """
        SELECT title, time_span, category, date
        FROM `{table}`
        WHERE username = @username
          AND category = @category
        ORDER BY date DESC
    """.format(table=TABLE)

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("user_id", "STRING", user_id),
            bigquery.ScalarQueryParameter("category", "STRING", category),
            bigquery.ScalarQueryParameter("username", "STRING", username), 
        ]
    )

    results = get_client().query(query, job_config=job_config).result()
    return [dict(row) for row in results]


def get_daily_summary(user_id, date, username):
    """
    GET #4: Returns total minutes spent per category for a user on a given date.
    e.g. get_daily_summary('user1', '2026-02-23')
    """
    query = """
        SELECT category, SUM(time_span) AS total_minutes
        FROM `{table}`
        WHERE username = @username
          AND date = @date
        GROUP BY category
        ORDER BY total_minutes DESC
    """.format(table=TABLE)

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("user_id", "STRING", user_id),
            bigquery.ScalarQueryParameter("date", "DATE", str(date)),
            bigquery.ScalarQueryParameter("username", "STRING", username), 
        ]
    )

    results = get_client().query(query, job_config=job_config).result()
    return [dict(row) for row in results]


def get_genai_advice(user_id, username):
    """
    GenAI: Fetches today's activity summary from BigQuery then uses
    Vertex AI to generate a personalised suggestion for the user.
    """
    today = str(date.today())
    summary = get_daily_summary(user_id, today, username)

    if not summary:
        summary_text = "No activities logged today."
    else:
        lines = [f"- {row['category']}: {row['total_minutes']} minutes" for row in summary]
        summary_text = "\n".join(lines)

    vertexai.init(project=PROJECT_ID, location=REGION)
    model = GenerativeModel("gemini-2.5-flash")

    prompt = f"""
    A student has logged the following activities today:
    {summary_text}

    Give them 2-3 short, friendly, and practical suggestions to improve
    their productivity and wellbeing based on this data. Keep it concise.
    """

    response = model.generate_content(prompt)
    return {
        'content': response.text,
        'summary': summary,
        'date': today,
    }

def get_home_ai_overview(username):
    """
    GenAI: Fetches today's tasks and generates productivity advice
    to help the user maximise their day.
    """
    tasks = get_todays_tasks(username)

    if not tasks:
        prompt = """
        A student has no tasks logged for today yet.
        Give them 2-3 short, friendly and motivating suggestions to help them
        plan a productive day. Encourage them to set goals and stay focused.
        Keep it concise and uplifting.
        """
    else:
        done = [t['name_of_task'] for t in tasks if t['completion']]
        pending = [t['name_of_task'] for t in tasks if not t['completion']]

        done_text = ", ".join(done) if done else "none yet"
        pending_text = ", ".join(pending) if pending else "all done!"

        prompt = f"""
        A student has the following tasks today:
        - Completed: {done_text}
        - Still pending: {pending_text}

        Give them 2-3 short, friendly and practical suggestions on how to
        maximise their productivity and get through their remaining tasks.
        Be encouraging and specific to their task list. Keep it concise.
        """

    vertexai.init(project=PROJECT_ID, location=REGION)
    model = GenerativeModel("gemini-2.5-flash")
    response = model.generate_content(prompt)
    return response.text

def add_activity(user_id, title, time_span, category, activity_date, username):
    """
    POST: Inserts a new activity entry into the analyser_table.
    """
    import uuid
    query = """
        INSERT INTO `{table}`
        (user_id, entry_id, date, title, time_span, category, username)
        VALUES (@user_id, @entry_id, @date, @title, @time_span, @category, @username)
    """.format(table=TABLE)

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("user_id", "STRING", user_id),
            bigquery.ScalarQueryParameter("entry_id", "STRING", str(uuid.uuid4())),
            bigquery.ScalarQueryParameter("date", "DATE", str(activity_date)),
            bigquery.ScalarQueryParameter("title", "STRING", title),
            bigquery.ScalarQueryParameter("time_span", "FLOAT64", float(time_span)),
            bigquery.ScalarQueryParameter("category", "STRING", category),
            bigquery.ScalarQueryParameter("username", "STRING", username), 
        ]
    )

    get_client().query(query, job_config=job_config).result()
    return True, "Activity logged successfully."

def get_user_posts(user_id):
    """Returns a list of a user's posts. Kept for compatibility."""
    import random
    content = random.choice([
        'Had a great workout today!',
        'The AI really motivated me to push myself further, I ran 10 miles!',
    ])
    return [{
        'user_id': user_id,
        'post_id': 'post1',
        'timestamp': '2024-01-01 00:00:00',
        'content': content,
        'image': 'image_url',
    }]


def get_user_sensor_data(user_id, workout_id):
    """Returns sensor data. Kept for compatibility."""
    import random
    sensor_data = []
    sensor_types = ['accelerometer', 'gyroscope', 'pressure', 'temperature', 'heart_rate']
    for index in range(random.randint(5, 100)):
        random_minute = str(random.randint(0, 59)).zfill(2)
        timestamp = '2024-01-01 00:' + random_minute + ':00'
        sensor_data.append({
            'sensor_type': random.choice(sensor_types),
            'timestamp': timestamp,
            'data': random.random() * 100
        })
    return sensor_data


def get_user_workouts(user_id):
    """Returns user workouts. Kept for compatibility."""
    import random
    workouts = []
    for index in range(random.randint(1, 3)):
        workouts.append({
            'workout_id': f'workout{index}',
            'start_timestamp': '2024-01-01 00:00:00',
            'end_timestamp': '2024-01-01 00:30:00',
            'start_lat_lng': (1 + random.randint(0, 100) / 100, 4 + random.randint(0, 100) / 100),
            'end_lat_lng': (1 + random.randint(0, 100) / 100, 4 + random.randint(0, 100) / 100),
            'distance': random.randint(0, 200) / 10.0,
            'steps': random.randint(0, 20000),
            'calories_burned': random.randint(0, 100),
        })
    return workouts

def get_todays_tasks(username):
    """
    Returns all tasks for a user due today.
    Used on the home page task list and donut chart.
    """
    from datetime import date
    today = str(date.today())
    query = """
        SELECT name_of_task, task_id, category, due_date, completion
        FROM `joshua-stevenson-hu.team_purple_dataset.tasks_table`
        WHERE username = @username
          AND due_date = @today
        ORDER BY completion ASC
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("username", "STRING", username),
            bigquery.ScalarQueryParameter("today", "DATE", today),
        ]
    )
    results = get_client().query(query, job_config=job_config).result()
    return [dict(row) for row in results]


def get_upcoming_reminders(username, limit=3):
    """
    Returns the next N upcoming reminders for a user.
    Used on the home page reminders stack.
    """
    query = """
        SELECT title, type, date_time
        FROM `joshua-stevenson-hu.team_purple_dataset.notification_table`
        WHERE username = @username
          AND date_time >= CURRENT_DATETIME()
        ORDER BY date_time ASC
        LIMIT @limit
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("username", "STRING", username),
            bigquery.ScalarQueryParameter("limit", "INT64", limit),
        ]
    )
    results = get_client().query(query, job_config=job_config).result()
    return [dict(row) for row in results]


def add_task(username, name_of_task, category, due_date):
    """
    POST: Inserts a new task into the tasks_table.
    """
    import uuid
    query = """
        INSERT INTO `joshua-stevenson-hu.team_purple_dataset.tasks_table`
        (name_of_task, task_id, category, start_date, due_date, completion, username)
        VALUES (@name_of_task, @task_id, @category, @start_date, @due_date, false, @username)
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("name_of_task", "STRING", name_of_task),
            bigquery.ScalarQueryParameter("task_id", "INT64", abs(hash(str(uuid.uuid4()))) % 1000000),
            bigquery.ScalarQueryParameter("category", "STRING", category),
            bigquery.ScalarQueryParameter("start_date", "DATE", str(date.today())),
            bigquery.ScalarQueryParameter("due_date", "DATE", str(due_date)),
            bigquery.ScalarQueryParameter("username", "STRING", username),
        ]
    )
    get_client().query(query, job_config=job_config).result()
    return True, "Task added successfully!"
