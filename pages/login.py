import streamlit as st
from helper.constants import auth_styles
from helper.utils import login_user
import time



def display_login_page():
    auth_styles()

    st.set_page_config(page_title="Login", layout="centered")
    st.markdown('<div class="app-title">Welcome to Productivity App</div>', unsafe_allow_html=True)

    with st.form("login_form"):
        username = st.text_input(
            "Username",
            placeholder="Enter your username"
        )
        password = st.text_input(
            "Password",
            type="password",
            placeholder="Enter your password"
        )

        col1, col2 = st.columns([1, 1])
        with col1:
            remember_me = st.checkbox("Remember me")


        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            submit = st.form_submit_button("Login", use_container_width=True)

    st.markdown(
        '<div class="create-account">Don’t have an account?</div>',
        unsafe_allow_html=True
    )

    c1, c2, c3 = st.columns([1.4, 1, 1.4])
    with c1:
        go_signup = st.button("Create account", use_container_width=True)
    with c3:
        go_recovery = st.button("Forgot password?", use_container_width=True)


    if submit:
        with st.spinner("Logging in..."):
            success, message, user = login_user(username, password)

        if success:
            st.session_state.authenticated = True
            st.session_state.current_user = user
            st.rerun()
        else:
            st.error(message)

    if go_signup:
        st.session_state.auth_view = "signup"
        st.rerun()
    if go_recovery:
        st.session_state.auth_view = "recovery"
        st.rerun()