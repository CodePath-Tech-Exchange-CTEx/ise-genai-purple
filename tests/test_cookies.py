from helper import cookies as cookie_utils


class FakeCookies(dict):
    def __init__(self):
        super().__init__()
        self.saved = False

    def save(self):
        self.saved = True


def test_set_cookies_sets_token_and_saves(monkeypatch):
    fake_cookies = FakeCookies()
    user = {"id": "u1", "name": "Ike", "username": "ike"}

    monkeypatch.setattr(
        cookie_utils,
        "create_remember_token",
        lambda user_id, remember_me: ("raw-token", "2030-01-01"),
    )

    cookie_utils.set_cookies(fake_cookies, user, True)

    assert fake_cookies[cookie_utils.COOKIE_NAME] == "raw-token"
    assert fake_cookies.saved is True