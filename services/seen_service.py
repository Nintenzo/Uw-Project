import requests
import time

def last_seen(remember_user_token, user_session_identifier):
    url = "https://tubiit.circle.so/feed"
    cookies = {
        "remember_user_token": remember_user_token,
        "user_session_identifier": user_session_identifier,
    }

    response = requests.get(url, cookies=cookies)
    time.sleep(2)
    print("last seen mimicked")
    return