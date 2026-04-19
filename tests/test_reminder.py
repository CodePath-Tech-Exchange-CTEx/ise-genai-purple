"""
Updated Regression Tests for reminder.py
Run with: pytest tests/test_reminder.py
"""

from __future__ import annotations
import pytest
from datetime import datetime, timedelta
from streamlit.testing.v1 import AppTest
from unittest.mock import patch

from pages.reminder import format_date


# -------------------------
# Helpers
# -------------------------

def run_app():
    at = AppTest.from_file("pages/reminder.py")

    # Inject required session state BEFORE run
    at.session_state["current_user"] = {"username": "test_user"}
    at.session_state["choose_item_type"] = "All"

    return at.run()


# -------------------------
# Module 1: Initial Render & Formatting
# -------------------------

class TestInitialRender:
    def test_page_renders_title(self):
        at = run_app()
        assert at.title[0].value == "Reminders"

    def test_sort_by_defaults_to_date(self):
        at = run_app()
        assert at.selectbox(key="sort_by").value == "Date"

    def test_format_date_logic(self):
        dt = datetime(2026, 3, 23, 15, 30)
        formatted = format_date(dt)

        assert "03:30pm" in formatted
        assert "Monday" in formatted
        assert "3/23" in formatted

    def test_format_date_handles_none(self):
        assert format_date(None) == ""


# -------------------------
# Module 2: List Rendering
# -------------------------

class TestReminderRendering:

    @patch("helper.notification_data.get_notifications")
    def test_renders_single_reminder(self, mock_get):
        mock_get.return_value = [{
            "title": "Clean Room",
            "type": "Task",
            "date_time": datetime.now(),
            "repeat": False,
            "interval": 0
        }]

        at = run_app()
        assert any("Clean Room" in m.value for m in at.markdown)

    @patch("helper.notification_data.get_notifications")
    def test_empty_state_message(self, mock_get):
        mock_get.return_value = []

        at = run_app()
        assert any("Add Some Reminders" in x.value for x in at.info)

    @patch("helper.notification_data.get_notifications")
    def test_event_filtering(self, mock_get):
        mock_get.return_value = [
            {"title": "Event A", "type": "Event", "date_time": datetime.now(), "repeat": False, "interval": 0},
            {"title": "Task B", "type": "Task", "date_time": datetime.now(), "repeat": False, "interval": 0},
        ]

        at = AppTest.from_file("pages/reminder.py")
        at.session_state["current_user"] = {"username": "test_user"}
        at.session_state["choose_item_type"] = "Event"

        at.run()

        assert any("Event A" in m.value for m in at.markdown)
        assert not any("Task B" in m.value for m in at.markdown)

    @patch("helper.notification_data.get_notifications")
    def test_sorting_a_to_z(self, mock_get):
        mock_get.return_value = [
            {"title": "Zebra", "type": "Task", "date_time": datetime.now(), "repeat": False, "interval": 0},
            {"title": "Apple", "type": "Task", "date_time": datetime.now(), "repeat": False, "interval": 0},
        ]

        at = AppTest.from_file("pages/reminder.py")
        at.session_state["current_user"] = {"username": "test_user"}
        at.session_state["sort_by"] = "A to Z"

        at.run()

        titles = [m.value for m in at.markdown if "**" in m.value]
        assert "Apple" in titles[0]


# -------------------------
# Module 3: Edit Dialog
# -------------------------

class TestEditDialog:

    @patch("helper.notification_data.get_notifications")
    def test_edit_button_opens_dialog(self, mock_get):
        mock_get.return_value = [{
            "title": "Specific Task",
            "type": "Task",
            "date_time": datetime.now(),
            "repeat": True,
            "interval": 60
        }]

        at = run_app()

        at.button(key="edit_0").click().run()

        # Delete button inside dialog
        assert at.button(key="del_Specific Task") is not None

    @patch("helper.notification_data.get_notifications")
    def test_repeat_interval_display(self, mock_get):
        mock_get.return_value = [{
            "title": "Repeat Task",
            "type": "Task",
            "date_time": datetime.now(),
            "repeat": True,
            "interval": 120
        }]

        at = run_app()

        assert any("Every 2h" in m.value for m in at.markdown)

