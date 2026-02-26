import streamlit as st
from pages.home import display_home_page

def display_app_page():
    """Displays the home page of the app."""
    home_page = st.Page(display_home_page, title="Home", icon=":material/home:")

    pg = st.navigation([home_page])
    pg.run()



# This is the starting point for your app. You do not need to change these lines
if __name__ == '__main__':
    display_app_page()