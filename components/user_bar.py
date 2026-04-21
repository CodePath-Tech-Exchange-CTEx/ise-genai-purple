import streamlit as st
from helper.cookies import COOKIE_NAME
from helper.auth_persistence import delete_remember_token


def render_user_bar(cookies):
    user = st.session_state.current_user
    display_name = user["name"].strip() if user and user.get("name") else "User"
    avatar_letter = display_name[0].upper()

    st.markdown(
        """
        <style>
        .userbar {
            display: flex;
            justify-content: flex-end;
            align-items: center;
            gap: 0.75rem;
            padding: 0.25rem 0 0.75rem 0;
        }

        .avatar {
            width: 34px;
            height: 34px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 700;
            background-color: #e8eefc;
            color: #1f3c88;
            font-size: 0.95rem;
        }

        .username {
            font-weight: 600;
            font-size: 0.95rem;
        }

        div[data-testid="stHorizontalBlock"] .logout-col button {
            padding-left: 0.4rem;
            padding-right: 0.4rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    spacer, avatar_col, name_col, logout_col = st.columns([7.5, 0.7, 1.8, 0.8])

    with avatar_col:
        st.markdown(f'<div class="avatar">{avatar_letter}</div>', unsafe_allow_html=True)

    with name_col:
        st.markdown(
            f'<div style="height:34px; display:flex; align-items:center;" class="username">{display_name}</div>',
            unsafe_allow_html=True,
        )

    with logout_col:
        st.markdown('<div class="logout-col">', unsafe_allow_html=True)
        if st.button(
            "",
            icon=":material/logout:",
            key="logout_button",
            help="Logout",
            type="tertiary",
            width="content",
        ):
            if cookies.ready():
                raw_token = cookies.get(COOKIE_NAME)

                if raw_token:
                    delete_remember_token(raw_token)
                    del cookies[COOKIE_NAME]
                    cookies.save()
            st.session_state.authenticated = False
            st.session_state.current_user = None
            st.session_state.auth_view = "login"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)