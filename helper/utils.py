import streamlit as st
from datetime import datetime, timedelta

from datetime import datetime

def init_calendar_state():
    if "calendar_events" not in st.session_state:
        st.session_state.calendar_events = []

def add_event_to_state(title: str, start_dt: datetime, end_dt: datetime):
    init_calendar_state()

    if end_dt <= start_dt:
        return False, "End must be after start."

    st.session_state.calendar_events.append(
        {"title": title, "start": start_dt.isoformat(), "end": end_dt.isoformat()}
    )
    return True, None


@st.dialog("Add event")
def add_event_dialog():
    title = st.text_input("Title", value="Event 1", key="Title")

    default_start = datetime.now().replace(minute=0, second=0, microsecond=0)
    default_end = default_start + timedelta(hours=1)

    start_date = st.date_input("Start date", value=default_start.date(), key="Start date")
    start_time = st.time_input("Start time", value=default_start.time(), key="Start time")

    end_date = st.date_input("End date", value=default_end.date(), key="End date")
    end_time = st.time_input("End time", value=default_end.time(), key="End time")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Save", type="primary", key="Save"):
            start_dt = datetime.combine(start_date, start_time)
            end_dt = datetime.combine(end_date, end_time)

            success, error = add_event_to_state(title, start_dt, end_dt)

            if not success:
                st.error(error)
            else:
                st.rerun()

    with col2:
        if st.button("Cancel", key="Cancel"):
            st.rerun()


def add_event_button():
    if st.button("➕ Add event", key="➕ Add event"):
        add_event_dialog()