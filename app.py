#############################################################################
# app.py
#
# This file contains the entrypoint for the app.
#
#############################################################################

import streamlit as st
from pages.reminder_page import display_reminder_page

def display_app_page():
    """Displays the reminder page of the app."""
    reminder_page = st.Page(display_reminder_page, title="Reminders", icon=":material/home:")

    pg = st.navigation([reminder_page])
    pg.run()



# This is the starting point for your app. You do not need to change these lines
if __name__ == '__main__':
    display_app_page()