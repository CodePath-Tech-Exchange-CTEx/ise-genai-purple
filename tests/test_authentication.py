from types import SimpleNamespace
import pytest

from helper import user_utils, auth_persistence
from datetime import datetime, timezone, timedelta


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


def test_username_exists_true(monkeypatch):
    fake_client = FakeClient(rows=[SimpleNamespace(username="ike")])
    monkeypatch.setattr(user_utils, "get_client", lambda: fake_client)

    assert user_utils.username_exists("ike") is True
    assert "FROM `joshua-stevenson-hu.team_purple_dataset.users_table`" in fake_client.last_query


def test_username_exists_false(monkeypatch):
    fake_client = FakeClient(rows=[])
    monkeypatch.setattr(user_utils, "get_client", lambda: fake_client)

    assert user_utils.username_exists("ike") is False


def test_create_user_rejects_blank_fields(monkeypatch):
    ok, msg, user = user_utils.create_user("", "ike", "password123")

    assert ok is False
    assert msg == "All fields are required."
    assert user is None


def test_create_user_rejects_existing_username(monkeypatch):
    monkeypatch.setattr(user_utils, "username_exists", lambda username: True)

    ok, msg, user = user_utils.create_user("Ike", "ike", "password123")

    assert ok is False
    assert msg == "Username already exists."
    assert user is None


def test_create_user_inserts_and_returns_user(monkeypatch):
    fake_client = FakeClient()
    monkeypatch.setattr(user_utils, "get_client", lambda: fake_client)
    monkeypatch.setattr(user_utils, "username_exists", lambda username: False)

    ok, msg, user = user_utils.create_user("Ike", "ike", "password123")

    assert ok is True
    assert msg == "Account created successfully."
    assert user is not None
    assert user["name"] == "Ike"
    assert user["username"] == "ike"
    assert "INSERT INTO `joshua-stevenson-hu.team_purple_dataset.users_table`" in fake_client.last_query


def test_login_user_rejects_blank_fields():
    ok, msg, user = user_utils.login_user("", "")

    assert ok is False
    assert msg == "Please enter both username and password."
    assert user is None


def test_login_user_rejects_missing_user(monkeypatch):
    fake_client = FakeClient(rows=[])
    monkeypatch.setattr(user_utils, "get_client", lambda: fake_client)

    ok, msg, user = user_utils.login_user("ike", "password123")

    assert ok is False
    assert msg == "Invalid username."
    assert user is None


def test_login_user_rejects_bad_password(monkeypatch):
    salt, password_hash = user_utils.hash_password("correct-password")

    fake_client = FakeClient(rows=[
        SimpleNamespace(
            id="user_1",
            name="Ike",
            username="ike",
            password_salt=salt,
            password_hash=password_hash,
        )
    ])
    monkeypatch.setattr(user_utils, "get_client", lambda: fake_client)

    ok, msg, user = user_utils.login_user("ike", "wrong-password")

    assert ok is False
    assert msg == "Invalid password."
    assert user is None


def test_login_user_accepts_valid_password(monkeypatch):
    salt, password_hash = user_utils.hash_password("password123")

    fake_client = FakeClient(rows=[
        SimpleNamespace(
            id="user_1",
            name="Ike",
            username="ike",
            password_salt=salt,
            password_hash=password_hash,
        )
    ])
    monkeypatch.setattr(user_utils, "get_client", lambda: fake_client)

    ok, msg, user = user_utils.login_user("ike", "password123")

    assert ok is True
    assert msg == "Login successful."
    assert user == {
        "id": "user_1",
        "name": "Ike",
        "username": "ike",
    }


def test_create_remember_token_inserts_token(monkeypatch):
    fake_client = FakeClient()
    monkeypatch.setattr(auth_persistence, "get_client", lambda: fake_client)

    raw_token, expires_at = auth_persistence.create_remember_token("user_1", remember_me=False)

    assert isinstance(raw_token, str)
    assert expires_at > datetime.now(timezone.utc)
    assert "INSERT INTO `joshua-stevenson-hu.team_purple_dataset.remember_tokens`" in fake_client.last_query


def test_get_user_from_remember_token_returns_user(monkeypatch):
    fake_client = FakeClient(rows=[
        SimpleNamespace(id="user_1", name="Ike", username="ike")
    ])
    monkeypatch.setattr(auth_persistence, "get_client", lambda: fake_client)

    user = auth_persistence.get_user_from_remember_token("raw-token-value")

    assert user == {
        "id": "user_1",
        "name": "Ike",
        "username": "ike",
    }


def test_delete_remember_token_runs_delete(monkeypatch):
    fake_client = FakeClient()
    monkeypatch.setattr(auth_persistence, "get_client", lambda: fake_client)

    auth_persistence.delete_remember_token("raw-token-value")

    assert "DELETE FROM `joshua-stevenson-hu.team_purple_dataset.remember_tokens`" in fake_client.last_query

def test_verify_password_returns_true_for_matching_password():
    salt, password_hash = user_utils.hash_password("password123")

    assert user_utils.verify_password("password123", salt, password_hash) is True


def test_verify_password_returns_false_for_wrong_password():
    salt, password_hash = user_utils.hash_password("password123")

    assert user_utils.verify_password("wrong-password", salt, password_hash) is False


def test_hash_password_generates_different_salts_for_same_password():
    salt1, hash1 = user_utils.hash_password("password123")
    salt2, hash2 = user_utils.hash_password("password123")

    assert salt1 != salt2
    assert hash1 != hash2


def test_set_user_sets_session_state():
    import streamlit as st

    st.session_state.clear()

    user = {"id": "u1", "name": "Ike", "username": "ike"}
    user_utils.set_user(user)

    assert st.session_state.authenticated is True
    assert st.session_state.current_user == user