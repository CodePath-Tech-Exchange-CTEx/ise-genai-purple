import streamlit as st
from datetime import datetime, timedelta
from google.cloud import bigquery
import time
import uuid
from helper.calendar_vertex_ai_utils import parse_event_with_vertex_ai

def get_client():
    return bigquery.Client()


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

    get_client().query(query, job_config=job_config).result()
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

    get_client().query(query, job_config=job_config).result()
    return True, "Event updated."

def delete_event_from_table(event_id: str):
    query = """
    DELETE FROM `joshua-stevenson-hu.team_purple_dataset.events_table`
    WHERE id = @id
    """

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("id", "STRING", event_id),
        ]
    )

    get_client().query(query, job_config=job_config).result()
    return True, "Event deleted."

def save_or_update_event(is_edit, event_data, title, start_dt, end_dt):
    if is_edit:
        return update_event_in_table(event_data["id"], title, start_dt, end_dt)
    return add_event_to_table(title, start_dt, end_dt)


def handle_save_button(is_edit, event_data, title, start_date, start_time, end_date, end_time):
    start_dt = datetime.combine(start_date, start_time)
    end_dt = datetime.combine(end_date, end_time)

    with st.spinner("Updating event..." if is_edit else "Saving event..."):
        success, message = save_or_update_event(
            is_edit, event_data, title, start_dt, end_dt
        )

    if success:
        st.toast(f"Event {'updated' if is_edit else 'saved'} successfully 🎉")
        time.sleep(1)
        st.rerun()
    else:
        st.error(message)


def handle_delete_confirmation(event_id, unique_key):
    st.warning("Are you sure you want to delete this event?")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Yes, delete", type="primary", key=f"confirm_delete_{unique_key}"):
            with st.spinner("Deleting event..."):
                success, message = delete_event_from_table(event_id)

            if success:
                st.toast("Event deleted successfully 🗑️")
                st.session_state[f"show_delete_confirm_{unique_key}"] = False
                time.sleep(1)
                st.rerun()
            else:
                st.error(message)

    with col2:
        if st.button("No, keep it", key=f"cancel_delete_{unique_key}"):
            st.session_state[f"show_delete_confirm_{unique_key}"] = False
            st.rerun()

@st.dialog("Event")
def event_dialog(event_data=None, ai_prefill=None):
    is_edit = event_data is not None

    if is_edit:
        default_title = event_data["title"]
        default_start = datetime.fromisoformat(event_data["start"])
        default_end = datetime.fromisoformat(event_data["end"])
        unique_key = event_data["id"]

    elif ai_prefill is not None:
        default_title = ai_prefill["title"]
        default_start = datetime.strptime(
            f"{ai_prefill['start_date']} {ai_prefill['start_time']}",
            "%Y-%m-%d %H:%M"
        )
        default_end = datetime.strptime(
            f"{ai_prefill['end_date']} {ai_prefill['end_time']}",
            "%Y-%m-%d %H:%M"
        )
        unique_key = "ai"

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

    actions_left, actions_right = st.columns([2, 1])

    with actions_left:
        update_col, delete_col, spacer_col = st.columns([1, 1, 1])

        with update_col:
            if st.button(
                "Update" if is_edit else "Save",
                type="primary",
                key=f"submit_{unique_key}",
                use_container_width=True
            ):
                handle_save_button(
                    is_edit, event_data, title,
                    start_date, start_time, end_date, end_time
                )

        with delete_col:
            if is_edit:
                if st.button(
                    "Delete",
                    key=f"delete_{unique_key}",
                    use_container_width=True
                ):
                    st.session_state[f"show_delete_confirm_{unique_key}"] = True

    with actions_right:
        if st.button(
            "Cancel",
            key=f"cancel_{unique_key}",
            use_container_width=True
        ):
            st.session_state[f"show_delete_confirm_{unique_key}"] = False
            st.rerun()

    if is_edit and st.session_state.get(f"show_delete_confirm_{unique_key}", False):
        handle_delete_confirmation(event_data["id"], unique_key)


def add_event_button():
    st.subheader("Create Event")

    left_col, right_col = st.columns([1, 2], vertical_alignment="bottom")

    with left_col:
        st.write("")
        if st.button("➕ Add manually", use_container_width=True):
            event_dialog()

    with right_col:

        with st.form("ai_event_form", clear_on_submit=False):
            user_text = st.text_input(
                "Create your event quicker with AI",
                placeholder="e.g. Meeting tomorrow at 2 PM for 1 hour",
                key="ai_event_prompt"
            )

            submitted = st.form_submit_button(
                "✨ Create with AI",
                use_container_width=True
            )

        if submitted:
            if not user_text.strip():
                st.warning("Please describe your event first.")
            else:
                try:
                    with st.spinner("Thinking..."):
                        parsed = parse_event_with_vertex_ai(user_text)
                    event_dialog(ai_prefill=parsed)
                except Exception as e:
                    st.error(f"AI failed: {e}")


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
    query_events = get_client().query(query).result()
    return turn_to_right_format(query_events)