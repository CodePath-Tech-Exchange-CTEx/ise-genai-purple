#############################################################################
# home.py
#
# This file is the home page of the app.
#
#############################################################################


import streamlit as st
from helper.constants import calendar_options, custom_css
from helper.utils import init_calendar_state
from streamlit_calendar import calendar
from helper.utils import add_event_button


def display_home_page():
    """Displays the home page of the app."""
    init_calendar_state()
    display_calendar(st.session_state.calendar_events, calendar_options, custom_css)

def display_calendar(calendar_events, calendar_options, custom_css):
    """Displays the calendar UI to see events in this productivity app
    
    calendar_events: Events that have been created in app's calendar
    calendar_options: Custom options to specify calendar attributes
    custom_css: Custom styling for calendar
    """
    add_event_button()
    calendar_ui = calendar(
        events=calendar_events,
        options=calendar_options,
        custom_css=custom_css,
        key='calendar',
    )

if __name__ == '__main__':
    display_home_page()
