import streamlit as st
from helper.constants import auth_styles
from helper.user_utils import login_user, set_user
import time
from helper.auth_persistence import create_remember_token
from helper.cookies import set_cookies


def display_login_page(cookies):
    auth_styles()

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

        with col2:
            st.markdown(
                '<div class="forgot-wrapper"><span class="forgot-link">Forgot password?</span></div>',
                unsafe_allow_html=True,
            )

        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            submit = st.form_submit_button("Login", use_container_width=True)

    st.markdown(
        '<div class="create-account">Don’t have an account?</div>',
        unsafe_allow_html=True
    )

    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        go_signup = st.button("Create account", use_container_width=True)

    if submit:
        with st.spinner("Logging in..."):
            success, message, user = login_user(username, password)

        if success:
            set_user(user)
            set_cookies(cookies, user, remember_me)
            st.rerun()
        else:
            st.error(message)

    if go_signup:
        st.session_state.auth_view = "signup"
        st.rerun()