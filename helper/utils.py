import streamlit as st
from datetime import datetime, timedelta
from google.cloud import bigquery
import time
import uuid

client = bigquery.Client()


def add_event_to_table(title: str, start_dt: datetime, end_dt: datetime):
    if end_dt <= start_dt:
        return False, "End must be after start."

    query = """
    INSERT INTO `joshua-stevenson-hu.team_purple_dataset.events_table`
    (id, title, start_date_time, end_date_time)
    VALUES (@id, @title, @start_dt, @end_dt)
    """

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("id", "STRING", str(uuid.uuid4())),
            bigquery.ScalarQueryParameter("title", "STRING", title),
            bigquery.ScalarQueryParameter("start_dt", "DATETIME", start_dt),
            bigquery.ScalarQueryParameter("end_dt", "DATETIME", end_dt),
        ]
    )

    client.query(query, job_config=job_config).result()
    return True, "Event added."


def update_event_in_table(event_id: str, title: str, start_dt: datetime, end_dt: datetime):
    if end_dt <= start_dt:
        return False, "End must be after start."

    query = """
    UPDATE `joshua-stevenson-hu.team_purple_dataset.events_table`
    SET title = @title,
        start_date_time = @start_dt,
        end_date_time = @end_dt
    WHERE id = @id
    """

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("id", "STRING", event_id),
            bigquery.ScalarQueryParameter("title", "STRING", title),
            bigquery.ScalarQueryParameter("start_dt", "DATETIME", start_dt),
            bigquery.ScalarQueryParameter("end_dt", "DATETIME", end_dt),
        ]
    )

    client.query(query, job_config=job_config).result()
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
                        event_data["id"], title, start_dt, end_dt
                    )
                else:
                    success, message = add_event_to_table(title, start_dt, end_dt)

            if success:
                st.toast(f"Event {"updated" if is_edit else "saved"} successfully 🎉")
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


def get_calendar_events():
    query = """
    SELECT id, title, start_date_time, end_date_time
    FROM `joshua-stevenson-hu.team_purple_dataset.events_table`
    """
    query_events = client.query(query).result()
    return turn_to_right_format(query_events)