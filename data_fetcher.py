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
PROJECT_ID = "joshua-stevenson-hu"
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


def get_user_activities(user_id, date):
    """
    GET #1: Returns all activity entries for a specific user on a given date.
    e.g. get_user_activities('user1', '2026-02-23')
    """
    query = """
        SELECT title, time_span, category, date
        FROM `{table}`
        WHERE user_id = @user_id
          AND date = @date
        ORDER BY time_span DESC
    """.format(table=TABLE)

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("user_id", "STRING", user_id),
            bigquery.ScalarQueryParameter("date", "DATE", str(date)),
        ]
    )

    results = get_client().query(query, job_config=job_config).result()
    return [dict(row) for row in results]


def get_activity_history(user_id, days=7):
    """
    GET #2: Returns all activities for a user over the last N days.
    e.g. get_activity_history('user1', days=7)
    """
    query = """
        SELECT title, time_span, category, date
        FROM `{table}`
        WHERE user_id = @user_id
          AND date >= DATE_SUB(CURRENT_DATE(), INTERVAL @days DAY)
        ORDER BY date DESC
    """.format(table=TABLE)

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("user_id", "STRING", user_id),
            bigquery.ScalarQueryParameter("days", "INT64", days),
        ]
    )

    results = get_client().query(query, job_config=job_config).result()
    return [dict(row) for row in results]


def get_activities_by_category(user_id, category):
    """
    GET #3: Returns all activities for a user filtered by category.
    e.g. get_activities_by_category('user1', 'Productive')
    """
    query = """
        SELECT title, time_span, category, date
        FROM `{table}`
        WHERE user_id = @user_id
          AND category = @category
        ORDER BY date DESC
    """.format(table=TABLE)

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("user_id", "STRING", user_id),
            bigquery.ScalarQueryParameter("category", "STRING", category),
        ]
    )

    results = get_client().query(query, job_config=job_config).result()
    return [dict(row) for row in results]


def get_daily_summary(user_id, date):
    """
    GET #4: Returns total minutes spent per category for a user on a given date.
    e.g. get_daily_summary('user1', '2026-02-23')
    """
    query = """
        SELECT category, SUM(time_span) AS total_minutes
        FROM `{table}`
        WHERE user_id = @user_id
          AND date = @date
        GROUP BY category
        ORDER BY total_minutes DESC
    """.format(table=TABLE)

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("user_id", "STRING", user_id),
            bigquery.ScalarQueryParameter("date", "DATE", str(date)),
        ]
    )

    results = get_client().query(query, job_config=job_config).result()
    return [dict(row) for row in results]


def get_genai_advice(user_id):
    """
    GenAI: Fetches today's activity summary from BigQuery then uses
    Vertex AI to generate a personalised suggestion for the user.
    """
    today = str(date.today())
    summary = get_daily_summary(user_id, today)

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

def add_activity(user_id, title, time_span, category, activity_date):
    """
    POST: Inserts a new activity entry into the analyser_table.
    """
    import uuid
    query = """
        INSERT INTO `{table}`
        (user_id, entry_id, date, title, time_span, category)
        VALUES (@user_id, @entry_id, @date, @title, @time_span, @category)
    """.format(table=TABLE)

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("user_id", "STRING", user_id),
            bigquery.ScalarQueryParameter("entry_id", "STRING", str(uuid.uuid4())),
            bigquery.ScalarQueryParameter("date", "DATE", str(activity_date)),
            bigquery.ScalarQueryParameter("title", "STRING", title),
            bigquery.ScalarQueryParameter("time_span", "FLOAT64", float(time_span)),
            bigquery.ScalarQueryParameter("category", "STRING", category),
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
