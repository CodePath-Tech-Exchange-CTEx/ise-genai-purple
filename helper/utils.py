import streamlit as st
from datetime import datetime, timedelta
from google.cloud import bigquery
import time
import uuid
import binascii
import os
import hashlib

def get_client():
    return bigquery.Client()


def add_event_to_table(title: str, start_dt: datetime, end_dt: datetime, user: str):
    if end_dt <= start_dt:
        return False, "End must be after start."

    query = """
    INSERT INTO `joshua-stevenson-hu.team_purple_dataset.events_table`
    (id, title, start_date_time, end_date_time, username)
    VALUES (@id, @title, @start_dt, @end_dt, @username)
    """

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("id", "STRING", str(uuid.uuid4())),
            bigquery.ScalarQueryParameter("title", "STRING", title),
            bigquery.ScalarQueryParameter("start_dt", "DATETIME", start_dt),
            bigquery.ScalarQueryParameter("end_dt", "DATETIME", end_dt),
            bigquery.ScalarQueryParameter("username", "STRING", user),
        ]
    )

    get_client().query(query, job_config=job_config).result()
    return True, "Event added."


def update_event_in_table(event_id: str, title: str, start_dt: datetime, end_dt: datetime, user: str):
    if end_dt <= start_dt:
        return False, "End must be after start."

    query = """
    UPDATE `joshua-stevenson-hu.team_purple_dataset.events_table`
    SET title = @title,
        start_date_time = @start_dt,
        end_date_time = @end_dt
    WHERE id = @id
    AND username = @username
    """

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("id", "STRING", event_id),
            bigquery.ScalarQueryParameter("title", "STRING", title),
            bigquery.ScalarQueryParameter("start_dt", "DATETIME", start_dt),
            bigquery.ScalarQueryParameter("end_dt", "DATETIME", end_dt),
            bigquery.ScalarQueryParameter("username", "STRING", user),
        ]
    )

    get_client().query(query, job_config=job_config).result()
    return True, "Event updated."


@st.dialog("Event")
def event_dialog(event_data=None):
    is_edit = event_data is not None

    if is_edit:
        default_title = event_data["title"]
        default_start = datetime.fromisoformat(event_data["start"])
        default_end = datetime.fromisoformat(event_data["end"])
        unique_key = event_data["id"]
    else:
        default_title = "Event 1"
        default_start = datetime.now().replace(minute=0, second=0, microsecond=0)
        default_end = default_start + timedelta(hours=1)
        unique_key = "new"

    title = st.text_input("Title", value=default_title, key=f"title_{unique_key}")

    start_date = st.date_input("Start date", value=default_start.date(), key=f"start_date_{unique_key}")
    start_time = st.time_input("Start time", value=default_start.time(), key=f"start_time_{unique_key}")

    end_date = st.date_input("End date", value=default_end.date(), key=f"end_date_{unique_key}")
    end_time = st.time_input("End time", value=default_end.time(), key=f"end_time_{unique_key}")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Update" if is_edit else "Save", type="primary", key=f"submit_{unique_key}"):
            start_dt = datetime.combine(start_date, start_time)
            end_dt = datetime.combine(end_date, end_time)

            with st.spinner("Updating event..." if is_edit else "Saving event..."):
                if is_edit:
                    success, message = update_event_in_table(
                        event_data["id"], title, start_dt, end_dt, st.session_state.current_user["username"]
                    )
                else:
                    success, message = add_event_to_table(title, start_dt, end_dt, st.session_state.current_user["username"])

            if success:
                st.toast(f"Event {'updated' if is_edit else 'saved'} successfully 🎉")
                time.sleep(1)
                st.rerun()
            else:
                st.error(message)

    with col2:
        if st.button("Cancel", key=f"cancel_{unique_key}"):
            st.rerun()


def add_event_button():
    if st.button("➕ Add event", key="➕ Add event"):
        event_dialog()


def turn_to_right_format(query_events):
    events = []

    for event in query_events:
        events.append({
            "id": event.id,
            "title": event.title,
            "start": event.start_date_time.isoformat(),
            "end": event.end_date_time.isoformat()
        })

    return events


def get_calendar_events(user):
    query = """
    SELECT id, title, start_date_time, end_date_time
    FROM `joshua-stevenson-hu.team_purple_dataset.events_table`
    WHERE username = @username
    """

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("username", "STRING", user),
        ]
    )

    query_events = get_client().query(query, job_config=job_config).result()
    return turn_to_right_format(query_events)

def hash_password(password: str):
    salt = os.urandom(16)
    derived_key = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        200_000,
    )
    return binascii.hexlify(salt).decode(), binascii.hexlify(derived_key).decode()


def verify_password(password: str, salt_hex: str, stored_hash_hex: str):
    salt = binascii.unhexlify(salt_hex.encode())
    derived_key = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        200_000,
    )
    return binascii.hexlify(derived_key).decode() == stored_hash_hex


def username_exists(username: str):
    query = """
    SELECT username
    FROM `joshua-stevenson-hu.team_purple_dataset.users_table`
    WHERE username = @username
    LIMIT 1
    """

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("username", "STRING", username),
        ]
    )

    rows = list(get_client().query(query, job_config=job_config).result())
    return len(rows) > 0


def create_user(name: str, username: str, password: str):
    name = name.strip()
    username = username.strip().lower()
    password = password.strip()

    if not name or not username or not password:
        return False, "All fields are required.", None

    try:
        if username_exists(username):
            return False, "Username already exists.", None

        salt, password_hash = hash_password(password)
        user_id = str(uuid.uuid4())

        query = """
        INSERT INTO `joshua-stevenson-hu.team_purple_dataset.users_table`
        (id, name, username, password_salt, password_hash)
        VALUES (@id, @name, @username, @password_salt, @password_hash)
        """

        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("id", "STRING", user_id),
                bigquery.ScalarQueryParameter("name", "STRING", name),
                bigquery.ScalarQueryParameter("username", "STRING", username),
                bigquery.ScalarQueryParameter("password_salt", "STRING", salt),
                bigquery.ScalarQueryParameter("password_hash", "STRING", password_hash),
            ]
        )

        get_client().query(query, job_config=job_config).result()

        user = {
            "id": user_id,
            "name": name,
            "username": username,
        }
        return True, "Account created successfully.", user

    except Exception as e:
        print(e)
        return False, "Something went wrong while creating the account.", None


def login_user(username: str, password: str):
    username = username.strip().lower()
    password = password.strip()

    if not username or not password:
        return False, "Please enter both username and password.", None

    query = """
    SELECT id, name, username, password_salt, password_hash
    FROM `joshua-stevenson-hu.team_purple_dataset.users_table`
    WHERE username = @username
    LIMIT 1
    """

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("username", "STRING", username),
        ]
    )

    try:
        rows = list(get_client().query(query, job_config=job_config).result())

        if not rows:
            return False, "Invalid username.", None

        user = rows[0]

        if not verify_password(password, user.password_salt, user.password_hash):
            return False, "Invalid password.", None

        return True, "Login successful.", {
            "id": user.id,
            "name": user.name,
            "username": user.username,
        }
    except Exception as e:
        print("Error", e)
        return False, "Something went wrong during login.", None