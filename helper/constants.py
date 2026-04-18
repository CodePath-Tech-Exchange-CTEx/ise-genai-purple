import streamlit as st

calendar_options = {
    "editable": True,
    "selectable": True,
    "headerToolbar": {
        "left": "today prev,next",
        "center": "title",
        "right": "timeGridDay,timeGridWeek",
    },
    "initialView": "timeGridWeek",
    "slotMinTime": "00:00:00",
    "slotMaxTime": "24:00:00",
    "nowIndicator": True,
    "allDaySlot": False,
    "slotDuration": "00:30:00",
    "slotLabelInterval": "01:00:00",
}

custom_css="""
    .fc-event-past {
        opacity: 0.8;
    }
    .fc-event-time {
        font-style: italic;
    }
    .fc-event-title {
        font-weight: 700;
    }
    .fc-toolbar-title {
        font-size: 2rem;
    }
"""

def auth_styles():
    st.markdown("""
    <style>
    .block-container {
        max-width: 550px;
        margin-top: 150px;
        margin-bottom: 150px;
        margin-left: auto;
        margin-right: auto;
        padding: 3rem 3rem 2.5rem 3rem;
        background: var(--secondary-background-color);
        color: var(--text-color);
        border-radius: 18px;
        box-shadow: 0 4px 18px rgba(0, 0, 0, 0.08);
    }

    .app-title {
        text-align: center;
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 2rem;
        color: var(--text-color);
    }

    .forgot-link, .create-link, .login-link {
        text-decoration: none;
        color: var(--primary-color);
        font-size: 0.95rem;
    }

    .forgot-wrapper {
        text-align: right;
        padding-top: 0.45rem;
    }

    .create-account, .bottom-link {
        text-align: center;
        margin-top: 1rem;
        font-size: 0.95rem;
        color: var(--text-color);
    }

    div[data-testid="stTextInput"] label,
    div[data-testid="stCheckbox"] label {
        color: var(--text-color) !important;
        font-weight: 500;
    }

    div[data-testid="stTextInput"] input {
        color: var(--text-color) !important;
        background-color: var(--background-color) !important;
        border: 1px solid rgba(128, 128, 128, 0.35) !important;
        border-radius: 0.5rem !important;
    }

    div[data-testid="stTextInput"] input::placeholder {
        color: rgba(128, 128, 128, 0.8) !important;
    }

    div[data-testid="stCheckbox"] p {
        color: var(--text-color) !important;
    }

    div.stButton button {
        background-color: var(--primary-color) !important;
        color: var(--background-color) !important;
        border: 1px solid rgba(128, 128, 128, 0.35) !important;
        border-radius: 0.5rem !important;
        font-weight: 500;
    }

    div.stButton > button:hover {
        filter: brightness(0.95);
    }
    </style>
    """, unsafe_allow_html=True)