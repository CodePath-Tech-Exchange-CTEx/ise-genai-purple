import streamlit as st
from helper import auto_login


class FakeCookies(dict):
    pass


def test_try_cookie_login_sets_user_when_token_valid(monkeypatch):
    st.session_state.clear()
    st.session_state.authenticated = False
    st.session_state.current_user = None

    fake_cookies = FakeCookies({"remember_token": "valid-token"})

    monkeypatch.setattr(
        auto_login,
        "get_user_from_remember_token",
        lambda token: {"id": "u1", "name": "Ike", "username": "ike"},
    )

    auto_login.try_cookie_login(fake_cookies)

    assert st.session_state.authenticated is True
    assert st.session_state.current_user == {
        "id": "u1",
        "name": "Ike",
        "username": "ike",
    }


def test_try_cookie_login_does_nothing_when_cookie_missing(monkeypatch):
    st.session_state.clear()
    st.session_state.authenticated = False
    st.session_state.current_user = None

    fake_cookies = FakeCookies()

    called = {"count": 0}

    def fake_lookup(token):
        called["count"] += 1
        return None

    monkeypatch.setattr(auto_login, "get_user_from_remember_token", fake_lookup)

    auto_login.try_cookie_login(fake_cookies)

    assert st.session_state.authenticated is False
    assert st.session_state.current_user is None
    assert called["count"] == 0


def test_try_cookie_login_does_nothing_when_token_invalid(monkeypatch):
    st.session_state.clear()
    st.session_state.authenticated = False
    st.session_state.current_user = None

    fake_cookies = FakeCookies({"remember_token": "bad-token"})

    monkeypatch.setattr(
        auto_login,
        "get_user_from_remember_token",
        lambda token: None,
    )

    auto_login.try_cookie_login(fake_cookies)

    assert st.session_state.authenticated is False
    assert st.session_state.current_user is None


def test_try_cookie_login_does_nothing_when_already_authenticated(monkeypatch):
    st.session_state.clear()
    st.session_state.authenticated = True
    st.session_state.current_user = {"id": "u1", "name": "Ike", "username": "ike"}

    fake_cookies = FakeCookies({"remember_token": "valid-token"})

    called = {"count": 0}

    def fake_lookup(token):
        called["count"] += 1
        return {"id": "u2", "name": "Other", "username": "other"}

    monkeypatch.setattr(auto_login, "get_user_from_remember_token", fake_lookup)

    auto_login.try_cookie_login(fake_cookies)

    assert st.session_state.current_user == {
        "id": "u1",
        "name": "Ike",
        "username": "ike",
    }
    assert called["count"] == 0