import streamlit as st
from pages.calendar import display_calendar_page
from pages.analyser import display_app_page as display_analyser_page
from pages.reminder import display_reminder_page
from pages.todo import display_todo_page
from pages.login import display_login_page
from pages.signup import display_signup_page
from components.user_bar import render_user_bar
from helper.auto_login import try_cookie_login
from streamlit_cookies_manager import EncryptedCookieManager


def display_app_page():
    """Displays the different pages of the app."""
    st.set_page_config(
        page_title="Productivity App",
        page_icon="📅",
    )

    cookies = EncryptedCookieManager(
        prefix="productivity_app/",
        password="productivity_app_cookies",
    )

    if not cookies.ready():
        st.write("Loading session...")
        st.stop()

    st.set_option("client.showSidebarNavigation", False)

    if st.session_state.get("show_signup_toast"):
        st.toast("Account created successfully 🎉")
        st.session_state.show_signup_toast = False

    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if "current_user" not in st.session_state:
        st.session_state.current_user = None

    if "auth_view" not in st.session_state:
        st.session_state.auth_view = "login"

    try_cookie_login(cookies)

    # Not logged in: render auth screens directly
    if not st.session_state.authenticated:
        if st.session_state.auth_view == "login":
            display_login_page(cookies)
        else:
            display_signup_page(cookies)
        return

    # Logged in: show actual app navigation
    calendar_page = st.Page(display_calendar_page, title="Calendar", icon=":material/calendar_month:")
    analyser_page = st.Page(display_analyser_page, title="Time Analyser", icon=":material/analytics:")
    reminder_page = st.Page(display_reminder_page, title="Reminders", icon=":material/alarm:")
    todo_page = st.Page(display_todo_page, title="Todo", icon=":material/check_circle:")

    render_user_bar(cookies)

    pg = st.navigation(
        [calendar_page, analyser_page, reminder_page, todo_page],
        position="top"
    )
    pg.run()


# This is the starting point for your app. You do not need to change these lines
if __name__ == '__main__':
    display_app_page()