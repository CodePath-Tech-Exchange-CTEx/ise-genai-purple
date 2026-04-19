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
        margin-left: auto;
        margin-right: auto;
        padding: 3rem 3rem 2.5rem 3rem;
        background: white;
        border-radius: 18px;
        box-shadow: 0 4px 18px rgba(0, 0, 0, 0.08);
    }

    .app-title {
        text-align: center;
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 2rem;
        color: #111827;
    }

    .forgot-link, .create-link, .login-link {
        text-decoration: none;
        color: #1f77b4;
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
        color: #374151;
    }

    /* labels */
    div[data-testid="stTextInput"] label,
    div[data-testid="stCheckbox"] label {
        color: #111827 !important;
        font-weight: 500;
    }

    /* input text */
    div[data-testid="stTextInput"] input {
        color: white !important;
    }

    /* placeholder text */
    div[data-testid="stTextInput"] input::placeholder {
        color: #d1d5db !important;
    }

    /* checkbox text */
    div[data-testid="stCheckbox"] p {
        color: #111827 !important;
    }
    </style>
    """, unsafe_allow_html=True)
