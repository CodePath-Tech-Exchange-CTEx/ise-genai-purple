import streamlit as st
from helper.constants import auth_styles
from helper.user_utils import create_user, set_user
import time
from helper.cookies import set_cookies

def display_signup_page(cookies):
    auth_styles()

    st.title("Sign Up")
    st.markdown('<div class="app-title">Sign Up</div>', unsafe_allow_html=True)

    with st.form("signup_form"):
        name = st.text_input("Name", placeholder="Enter your name")
        username = st.text_input("Username", placeholder="Choose a username")
        password = st.text_input("Password", type="password", placeholder="Create a password")
        confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm your password")

        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            submit = st.form_submit_button("Create Account", use_container_width=True)

    st.markdown(
        '<div class="bottom-link">Already have an account?</div>',
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
            with st.spinner("Creating account..."):
                success, message, user = create_user(name, username, password)

            if success:
                set_user(user)
                set_cookies(cookies, user, False)
                st.session_state.show_signup_toast = True
                st.rerun()
            else:
                st.error(message)

    if go_login:
        st.session_state.auth_view = "login"
        st.rerun()