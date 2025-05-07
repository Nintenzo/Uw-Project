from services.db_service import get_user_password
import time
import requests
def last_seen(email):
    try:
        remember_user_token, user_session_identifier = fresh_cookies(email)
        url = "https://tubiit.circle.so/feed"
        cookies = {
            "remember_user_token": remember_user_token,
            "user_session_identifier": user_session_identifier,
        }
        try:
            requests.get(url, cookies=cookies)
        except Exception:
            time.sleep(10)
            requests.get(url, cookies=cookies)
        time.sleep(2)
        print("last seen mimicked")
        return
    except Exception:
        pass

def fresh_cookies(email):
    pw = get_user_password(email)[0]
    payload = {
        "user": {
            "email": email,
            "password": pw,
            "community_id": ''
        },
        "source": None,
        "chat_bot_session_id": ""
    }

    session = requests.Session()
    link = "https://login.circle.so/sign_in?"
    session.headers.update({
            "accept": "application/json",
        })
    response = session.post(link, json=payload)
    link = response.json()['redirect_url']
    session.get(link, json=payload)
    return session.cookies['remember_user_token'], session.cookies['user_session_identifier']
