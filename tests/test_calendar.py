import sys
import types
from datetime import datetime
from types import SimpleNamespace

import pytest
from streamlit.testing.v1 import AppTest

from helper import utils
import pages.calendar as calendar_page


CALENDAR_PATH = "pages/calendar.py"


@pytest.fixture(autouse=True)
def stub_streamlit_calendar(monkeypatch):
    """
    streamlit_calendar is a custom component.
    AppTest does not always handle custom components well, so we stub it.
    """
    fake_mod = types.ModuleType("streamlit_calendar")

    def fake_calendar(*args, **kwargs):
        return {"mocked": True}

    fake_mod.calendar = fake_calendar
    monkeypatch.setitem(sys.modules, "streamlit_calendar", fake_mod)


def make_app():
    return AppTest.from_file(CALENDAR_PATH)


def assert_app_ok(at: AppTest):
    key = "$$STREAMLIT_INTERNAL_KEY_SCRIPT_RUN_WITHOUT_ERRORS"
    assert key in at.session_state and at.session_state[key] is True, (
        "App crashed during run. Scroll up to the traceback printed by pytest."
    )


class FakeQueryJob:
    def __init__(self, rows=None):
        self._rows = rows or []

    def result(self):
        return self._rows


class FakeClient:
    def __init__(self, rows=None):
        self.rows = rows or []
        self.last_query = None
        self.last_job_config = None

    def query(self, query, job_config=None):
        self.last_query = query
        self.last_job_config = job_config
        return FakeQueryJob(self.rows)


def test_calendar_page_renders(monkeypatch):
    monkeypatch.setattr(calendar_page, "get_calendar_events", lambda: [])

    at = make_app().run()
    assert_app_ok(at)

    assert len(at.title) == 1
    assert at.title[0].value == "📅 Calendar"


def test_add_event_button_is_present(monkeypatch):
    monkeypatch.setattr(calendar_page, "get_calendar_events", lambda: [])

    at = make_app().run()
    assert_app_ok(at)

    add_event_btn = at.button("➕ Add event")
    assert add_event_btn.label == "➕ Add event"


def test_add_event_to_table_invalid_does_not_query(monkeypatch):
    fake_client = FakeClient()
    monkeypatch.setattr(utils, "client", fake_client)

    start = datetime(2026, 2, 21, 12, 0)
    end = datetime(2026, 2, 21, 11, 0)

    ok, err = utils.add_event_to_table("Bad event", start, end)

    assert ok is False
    assert err == "End must be after start."
    assert fake_client.last_query is None
    assert fake_client.last_job_config is None


def test_add_event_to_table_valid_runs_insert_query(monkeypatch):
    fake_client = FakeClient()
    monkeypatch.setattr(utils, "client", fake_client)

    start = datetime(2026, 2, 21, 10, 0)
    end = datetime(2026, 2, 21, 11, 0)

    ok, err = utils.add_event_to_table("Study block", start, end)

    assert ok is True
    assert err == "Event added."
    assert fake_client.last_query is not None
    assert "INSERT INTO" in fake_client.last_query
    assert "events_table" in fake_client.last_query
    assert "(id, title, start_date_time, end_date_time)" in fake_client.last_query
    assert fake_client.last_job_config is not None
    assert len(fake_client.last_job_config.query_parameters) == 4


def test_update_event_in_table_invalid_does_not_query(monkeypatch):
    fake_client = FakeClient()
    monkeypatch.setattr(utils, "client", fake_client)

    start = datetime(2026, 2, 21, 14, 0)
    end = datetime(2026, 2, 21, 13, 0)

    ok, err = utils.update_event_in_table("evt_123", "Bad update", start, end)

    assert ok is False
    assert err == "End must be after start."
    assert fake_client.last_query is None
    assert fake_client.last_job_config is None


def test_update_event_in_table_valid_runs_update_query(monkeypatch):
    fake_client = FakeClient()
    monkeypatch.setattr(utils, "client", fake_client)

    start = datetime(2026, 2, 21, 15, 0)
    end = datetime(2026, 2, 21, 16, 0)

    ok, err = utils.update_event_in_table("evt_123", "Updated event", start, end)

    assert ok is True
    assert err == "Event updated."
    assert fake_client.last_query is not None
    assert "UPDATE" in fake_client.last_query
    assert "events_table" in fake_client.last_query
    assert "WHERE id = @id" in fake_client.last_query
    assert fake_client.last_job_config is not None
    assert len(fake_client.last_job_config.query_parameters) == 4


def test_turn_to_right_format_converts_rows():
    rows = [
        SimpleNamespace(
            id="evt_1",
            title="E-board Call",
            start_date_time=datetime(2026, 3, 9, 12, 30),
            end_date_time=datetime(2026, 3, 9, 13, 30),
        ),
        SimpleNamespace(
            id="evt_2",
            title="Event 1",
            start_date_time=datetime(2026, 3, 10, 15, 0),
            end_date_time=datetime(2026, 3, 10, 16, 0),
        ),
    ]

    events = utils.turn_to_right_format(rows)

    assert events == [
        {
            "id": "evt_1",
            "title": "E-board Call",
            "start": "2026-03-09T12:30:00",
            "end": "2026-03-09T13:30:00",
        },
        {
            "id": "evt_2",
            "title": "Event 1",
            "start": "2026-03-10T15:00:00",
            "end": "2026-03-10T16:00:00",
        },
    ]


def test_get_calendar_events_queries_and_formats_rows(monkeypatch):
    rows = [
        SimpleNamespace(
            id="evt_3",
            title="Meeting",
            start_date_time=datetime(2026, 3, 11, 9, 0),
            end_date_time=datetime(2026, 3, 11, 10, 0),
        ),
        SimpleNamespace(
            id="evt_4",
            title="Workshop",
            start_date_time=datetime(2026, 3, 11, 14, 0),
            end_date_time=datetime(2026, 3, 11, 15, 30),
        ),
    ]

    fake_client = FakeClient(rows=rows)
    monkeypatch.setattr(utils, "client", fake_client)

    events = utils.get_calendar_events()

    assert fake_client.last_query is not None
    assert "SELECT id, title, start_date_time, end_date_time" in fake_client.last_query

    assert events == [
        {
            "id": "evt_3",
            "title": "Meeting",
            "start": "2026-03-11T09:00:00",
            "end": "2026-03-11T10:00:00",
        },
        {
            "id": "evt_4",
            "title": "Workshop",
            "start": "2026-03-11T14:00:00",
            "end": "2026-03-11T15:30:00",
        },
    ]


def test_display_calendar_opens_event_dialog_on_event_click(monkeypatch):
    called = {}

    monkeypatch.setattr(calendar_page, "add_event_button", lambda: None)
    monkeypatch.setattr(calendar_page.st, "title", lambda *args, **kwargs: None)
    monkeypatch.setattr(calendar_page.st, "divider", lambda *args, **kwargs: None)

    def fake_event_dialog(event_data=None):
        called["event_data"] = event_data

    def fake_calendar(*args, **kwargs):
        return {
            "callback": "eventClick",
            "eventClick": {
                "event": {
                    "id": "evt_5",
                    "title": "Team Meeting",
                    "start": "2026-03-12T10:00:00",
                    "end": "2026-03-12T11:00:00",
                }
            },
        }

    monkeypatch.setattr(calendar_page, "event_dialog", fake_event_dialog)
    monkeypatch.setattr(calendar_page, "calendar", fake_calendar)

    calendar_page.display_calendar([], {}, "")

    assert "event_data" in called
    assert called["event_data"] == {
        "id": "evt_5",
        "title": "Team Meeting",
        "start": "2026-03-12T10:00:00",
        "end": "2026-03-12T11:00:00",
    }


def test_display_calendar_does_nothing_when_no_event_click(monkeypatch):
    called = {"count": 0}

    monkeypatch.setattr(calendar_page, "add_event_button", lambda: None)
    monkeypatch.setattr(calendar_page.st, "title", lambda *args, **kwargs: None)
    monkeypatch.setattr(calendar_page.st, "divider", lambda *args, **kwargs: None)

    def fake_event_dialog(event_data=None):
        called["count"] += 1

    def fake_calendar(*args, **kwargs):
        return {"mocked": True}

    monkeypatch.setattr(calendar_page, "event_dialog", fake_event_dialog)
    monkeypatch.setattr(calendar_page, "calendar", fake_calendar)

    calendar_page.display_calendar([], {}, "")

    assert called["count"] == 0