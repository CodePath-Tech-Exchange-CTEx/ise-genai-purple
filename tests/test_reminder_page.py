"""
Regression-style tests for reminder_page.py

Structure:
- One pytest class per "module" (feature area)
- Use widget *keys* instead of element list indexes

Notes:
- These tests use Streamlit's AppTest harness.
- reminder_page.py must be the filename of your app file.
- The Add Reminder button key is:
    - add_reminder
"""

from __future__ import annotations

from datetime import datetime
from streamlit.testing.v1 import AppTest


# -------------------------
# Helpers
# -------------------------

def run_app() -> AppTest:
    """Create a fresh Reminder app session and run once."""
    at = AppTest.from_file("pages/reminder_page.py").run()
    assert not at.exception
    return at


def ss_get(at: AppTest, key: str, default=None):
    """Safe session_state getter."""
    try:
        if key in at.session_state:
            return at.session_state[key]
    except Exception:
        pass

    try:
        return at.session_state[key]
    except Exception:
        return default


# -------------------------
# Module 1: Initial Render
# -------------------------

class TestInitialRender:
    def test_page_renders_title(self):
        at = run_app()
        assert at.title[0].value == "Reminders"

    def test_sort_by_defaults_to_date(self):
        at = run_app()
        assert ss_get(at, "sort_by") == "Date"

    def test_reminders_list_initialized(self):
        at = run_app()
        reminders = ss_get(at, "reminders_list")
        assert isinstance(reminders, list)
        assert reminders == []

    def test_empty_list_shows_error_message(self):
        at = run_app()
        assert at.error[0].value == "Add some reminders"


# -------------------------
# Module 2: Add Reminder Dialog
# -------------------------

class TestAddReminderModule:
    def test_add_button_opens_dialog(self):
        at = run_app()
        at.button(key="add_reminder").click().run()

        # Dialog should render input fields
        assert any(ti.label == "Reminder Name" for ti in at.text_input)

    def test_submit_with_empty_fields_shows_errors(self):
        at = run_app()

        at.button(key="add_reminder").click().run()
        at.button("Submit").click().run()

        errors = [e.value for e in at.error]
        assert "Title is required." in errors
        assert "Please select a priority level." in errors

    def test_valid_reminder_is_added_to_session_state(self):
        at = run_app()

        at.button(key="add_reminder").click().run()

        at.text_input(label="Reminder Name").input("Test Reminder").run()
        at.pills(label="Priority Level").select("Priority 1").run()

        at.button("Submit").click().run()

        reminders = ss_get(at, "reminders_list")
        assert len(reminders) == 1
        assert reminders[0]["title"] == "Test Reminder"
        assert reminders[0]["priority"] == "Priority 1"
        assert reminders[0]["completed"] is False


# -------------------------
# Module 3: Checkbox Completion
# -------------------------

class TestCompletionModule:
    def test_checkbox_marks_reminder_completed(self):
        at = run_app()

        # Inject reminder directly into session_state
        at.session_state["reminders_list"] = [{
            "title": "Checkbox Test",
            "date": datetime.now(),
            "priority": "Priority 2",
            "tag": None,
            "tag_color": "",
            "completed": False
        }]

        at.run()

        # Toggle checkbox
        at.checkbox(key="complete_0").set_value(True).run()

        reminders = ss_get(at, "reminders_list")
        assert reminders[0]["completed"] is True


# -------------------------
# Module 4: Clear Completed
# -------------------------

class TestClearCompletedModule:
    def test_clear_completed_removes_only_completed(self):
        at = run_app()

        at.session_state["reminders_list"] = [
            {
                "title": "Done",
                "date": datetime.now(),
                "priority": "Priority 1",
                "tag": None,
                "tag_color": "",
                "completed": True
            },
            {
                "title": "Not Done",
                "date": datetime.now(),
                "priority": "Priority 3",
                "tag": None,
                "tag_color": "",
                "completed": False
            }
        ]

        at.run()

        at.button("Clear Completed").click().run()

        reminders = ss_get(at, "reminders_list")
        assert len(reminders) == 1
        assert reminders[0]["title"] == "Not Done"

    def test_clear_completed_on_empty_list_does_not_crash(self):
        at = run_app()
        at.button("Clear Completed").click().run()
        assert not at.exception


# -------------------------
# Module 5: Date Formatting
# -------------------------

class TestFormatDate:
    def test_format_date_returns_string(self):
        at = run_app()

        dt = datetime(2024, 1, 15, 15, 30)
        formatted = at.module.format_date(dt)

        assert isinstance(formatted, str)
        assert "pm" in formatted.lower()

    def test_format_date_handles_none(self):
        at = run_app()
        formatted = at.module.format_date(None)
        assert formatted == ""