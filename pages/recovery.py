import streamlit as st
from helper.constants import auth_styles
from helper.user_utils import update_password
import time

def display_recovery_page():
    auth_styles()

    st.set_page_config(page_title="Password Recovery", layout="centered")
    st.markdown('<div class="app-title">Password Recovery</div>', unsafe_allow_html=True)

    with st.form("recovery_form"):
        username = st.text_input("Enter your username:", placeholder="Username")
        password = st.text_input("New Password:", type="password", placeholder="Create a new password")
        confirm_password = st.text_input("Confirm New Password:", type="password", placeholder="Confirm your new password")

        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            submit = st.form_submit_button("Update Password", use_container_width=True)

    st.markdown(
        '<div class="bottom-link">Remembered your password?</div>',
        unsafe_allow_html=True
    )

    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        go_login = st.button("Login", use_container_width=True)

    if submit:
        if password != confirm_password:
            st.error("Passwords do not match.")
        elif len(password) < 6:
            st.error("Password should be at least 6 characters.")
        else:
            with st.spinner("Updating password..."):
                success, message, user = update_password(username, password)

            if success:
                st.session_state.authenticated = True
                st.session_state.current_user = user
                st.session_state.show_signup_toast = True
                st.rerun()
            else:
                st.error(message)

    if go_login:
        st.session_state.auth_view = "login"
        st.rerun()