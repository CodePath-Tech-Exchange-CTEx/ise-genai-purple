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

    "slotMinTime": "06:00:00",
    "slotMaxTime": "18:00:00",

    "nowIndicator": True,
    "allDaySlot": False,
    "slotDuration": "00:30:00",
    "slotLabelInterval": "01:00",
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