from helper.auth_persistence import create_remember_token

COOKIE_NAME = "remember_token"

def set_cookies(cookies, user, remember_me):
    raw_token, expires_at = create_remember_token(user["id"], remember_me)
    cookies[COOKIE_NAME] = raw_token
    cookies.save()