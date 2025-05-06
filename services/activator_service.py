import requests
import bs4
from services.get_json_patch import get_patch_data
from services.create_email import get_messages

def send_otp(email, password):
    session = requests.Session()
    session.headers.update({
        "accept": "application/json",
    })

    payload = {
        "user": {
            "email": email,
            "password": password,
            "community_id": ''
        },
        "source": None,
        "chat_bot_session_id": ""
    }
    link = "https://login.circle.so/sign_in?"
    response = session.post(link, json=payload)
    link = response.json()['redirect_url']
    response = session.get(link)
    remember_user_token, user_session_identifier = session.cookies['remember_user_token'], session.cookies['user_session_identifier']
    cookies = {
        "remember_user_token": remember_user_token,
        "user_session_identifier": user_session_identifier
    }
    response = requests.get(link, cookies=cookies)
    soup = bs4.BeautifulSoup(response.text, "html.parser")
    auth_token_input = soup.find('input', {'name': 'authenticity_token'})
    authenticity_token = auth_token_input['value']
    payload = {'address': email,
            'password': password}
    otp = get_messages(payload)
    activate(authenticity_token, otp, cookies)
    return cookies

	
def activate(authenticity_token, otp, cookies):
    session = requests.Session()
    payload = {
        'authenticity_token': authenticity_token,
        'otp': otp,
        'source': ''
    }
    session.headers.update({
        'Content-Type': 'application/x-www-form-urlencoded',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'application/json',
        'Accept-Language': 'en-US,en;q=0.9',
        'Connection': 'keep-alive'
    })

    session.cookies.update(cookies) 
    
    url = 'https://login.circle.so/auth/otp_confirmations'
    session.post(url, data=payload)

    url = "https://tubiit.circle.so/internal_api/signup/profile?"
    response = requests.get(url, cookies=cookies)
    data = response.json()
    payload = get_patch_data(data)
    session = requests.put(url, cookies=cookies,json=payload)
