#############################################################################
# calendar.py
#
# This file is the calendar page of the app.
#
#############################################################################


import streamlit as st
from helper.constants import calendar_options, custom_css
from streamlit_calendar import calendar
from helper.calendar_utils import add_event_button, get_calendar_events, event_dialog


def display_calendar_page():
    """Displays the calendar page of the app."""
    display_calendar(get_calendar_events(), calendar_options, custom_css)

def display_calendar(calendar_events, calendar_options, custom_css):
    """Displays the calendar UI to see events in this productivity app
    
    calendar_events: Events that have been created in app's calendar
    calendar_options: Custom options to specify calendar attributes
    custom_css: Custom styling for calendar
    """
    st.title("📅 Calendar")
    st.divider()
    add_event_button()

    calendar_state = calendar(
        events=calendar_events,
        options=calendar_options,
        custom_css=custom_css,
        key="calendar",
    )

    if calendar_state and calendar_state.get("callback") == "eventClick":
        clicked_event = calendar_state["eventClick"]["event"]
        event_dialog(clicked_event)

if __name__ == '__main__':
    display_calendar_page()
