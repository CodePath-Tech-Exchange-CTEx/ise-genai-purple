import streamlit as st
from pages.calendar import display_calendar_page
from database.events import create_events_table
from pages.reminder import display_reminder_page

create_events_table()

def display_app_page():
    """Displays the different pages of the app."""
    st.set_page_config(
        page_title="Productivity App",
        page_icon="📅",
    )
    calendar_page = st.Page(display_calendar_page, title="Calendar", icon=":material/calendar_month:")
    reminder_page = st.Page(display_reminder_page, title="Reminders", icon=":material/alarm:")



    pg = st.navigation([calendar_page, reminder_page], position="top")
    pg.run()



# This is the starting point for your app. You do not need to change these lines
if __name__ == '__main__':
    display_app_page()