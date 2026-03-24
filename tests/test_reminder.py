"""
Consolidated Regression Tests for reminder.py
Run with: pytest tests/test_reminder.py
"""

from __future__ import annotations
import pytest
from datetime import datetime
from streamlit.testing.v1 import AppTest
from unittest.mock import patch

# Import your formatting function directly for unit testing
# Note: Ensure your python path includes the root directory
from pages.reminder import format_date

# -------------------------
# Helpers
# -------------------------

def run_app() -> AppTest:
    """Helper to initialize the AppTest harness."""
    at = AppTest.from_file("pages/reminder.py").run()
    return at

# -------------------------
# Module 1: Initial Render & Formatting
# -------------------------

class TestInitialRender:
    def test_page_renders_title(self):
        at = run_app()
        assert at.title[0].value == "Reminders"

    def test_sort_by_defaults_to_date(self):
        at = run_app()
        # Verify the selectbox key exists and defaults correctly
        assert at.selectbox(key="sort_by").value == "Date"

    def test_format_date_logic(self):
        """Tests the string replacement logic (AM -> am)."""
        dt = datetime(2026, 3, 23, 15, 30) # 3:30 PM
        formatted = format_date(dt)
        assert "03:30pm" in formatted
        assert "Monday" in formatted
        assert "3/23" in formatted

    def test_format_date_handles_none(self):
        assert format_date(None) == ""


# -------------------------
# Module 2: List Rendering & Edit Dialog
# -------------------------

class TestEditDeleteModule:
    @patch("helper.notification_data.get_notifications")
    def test_reminders_render_from_db(self, mock_get):
        """Verify UI displays data returned from BigQuery."""
        mock_get.return_value = [{
            "title": "Clean Room",
            "type": "Task",
            "date_time": datetime.now(),
            "repeat": False,
            "interval": 0
        }]
        
        at = run_app()
        # Check if the title is rendered in markdown
        assert any("Clean Room" in m.value for m in at.markdown)

    @patch("helper.notification_data.get_notifications")
    def test_edit_button_opens_correct_reminder(self, mock_get):
        mock_get.return_value = [{
            "title": "Specific Task",
            "type": "Task",
            "date_time": datetime.now(),
            "repeat": True,
            "interval": 60
        }]
        
        at = run_app()
        # Click the first '3-dots' button
        at.button(key="edit_0").click().run()
        
        # Check if the Delete button inside the dialog has the correct title-based key
        assert at.button(key="del_Specific Task") is not None
