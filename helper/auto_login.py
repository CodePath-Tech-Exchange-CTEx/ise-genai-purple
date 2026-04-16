import streamlit as st
from helper.auth_persistence import get_user_from_remember_token
from helper.cookies import COOKIE_NAME
from helper.user_utils import set_user


def try_cookie_login(cookies):
    raw_token = cookies.get(COOKIE_NAME)

    if raw_token and not st.session_state.authenticated:
        user = get_user_from_remember_token(raw_token)
        if user:
            set_user(user)