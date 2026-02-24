import sys
import types
from datetime import datetime, timedelta

import pytest
from streamlit.testing.v1 import AppTest

from helper import utils


HOME_PATH = "pages/home.py"


@pytest.fixture(autouse=True)
def stub_streamlit_calendar(monkeypatch):
    """
    streamlit_calendar is a custom component.
    AppTest doesn't always play nice with custom components, so we stub it.
    """
    fake_mod = types.ModuleType("streamlit_calendar")

    def fake_calendar(*args, **kwargs):
        return {"mocked": True}

    fake_mod.calendar = fake_calendar
    monkeypatch.setitem(sys.modules, "streamlit_calendar", fake_mod)


def make_app():
    return AppTest.from_file(HOME_PATH)


def assert_app_ok(at: AppTest):
    key = "$$STREAMLIT_INTERNAL_KEY_SCRIPT_RUN_WITHOUT_ERRORS"
    assert key in at.session_state and at.session_state[key] is True, \
        "App crashed during run. Scroll up to the traceback printed by pytest."


def test_home_page_renders_and_initializes_state():
    at = make_app().run()
    assert_app_ok(at)

    assert "calendar_events" in at.session_state
    assert at.session_state["calendar_events"] == []


def test_add_event_button_is_present():
    at = make_app().run()
    assert_app_ok(at)

    add_event_btn = at.button("➕ Add event")
    assert add_event_btn.label == "➕ Add event"


def test_add_event_to_state_valid_adds_event():
    utils.init_calendar_state()
    utils.st.session_state.calendar_events = []

    start = datetime(2026, 2, 21, 10, 0)
    end = datetime(2026, 2, 21, 11, 0)

    ok, err = utils.add_event_to_state("Study block", start, end)
    assert ok is True
    assert err is None

    assert len(utils.st.session_state.calendar_events) == 1
    event_state = utils.st.session_state.calendar_events[0]
    assert event_state["title"] == "Study block"
    assert event_state["start"] == start.isoformat()
    assert event_state["end"] == end.isoformat()


def test_add_event_to_state_invalid_does_not_add():
    utils.init_calendar_state()
    utils.st.session_state.calendar_events = []

    start = datetime(2026, 2, 21, 12, 0)
    end = datetime(2026, 2, 21, 11, 0)

    ok, err = utils.add_event_to_state("Bad event", start, end)
    assert ok is False
    assert err == "End must be after start."
    assert utils.st.session_state.calendar_events == []