import streamlit as st
from pages.calendar import display_calendar_page
from database.events import create_events_table
from pages.analyser import display_app_page as display_analyser_page

create_events_table()

def display_app_page():
    """Displays the different pages of the app."""
    st.set_page_config(
        page_title="Productivity App",
        page_icon="📅",
    )
    calendar_page = st.Page(display_calendar_page, title="Calendar", icon=":material/calendar_month:")
    analyser_page = st.Page(display_analyser_page, title="Time Analyser", icon=":material/analytics:")

    pg = st.navigation([calendar_page, analyser_page], position="top")
    pg.run()



# This is the starting point for your app. You do not need to change these lines
if __name__ == '__main__':
    display_app_page()
