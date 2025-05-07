from services.password_service import generate_password
import requests
import random
import string
import time
from dotenv import load_dotenv
load_dotenv()


base_url = 'https://api.mail.tm'


def get_domain():
    response = requests.get(f"{base_url}/domains")
    if response.status_code == 200:
        data = response.json()
        domain = data['hydra:member'][0]['domain']

    return "@"+domain


def generate_random_email():
    valid_username_chars = string.ascii_letters + string.digits + "._%-"
    username_length = random.randint(10, 15)
    username = ''.join(random.choices(valid_username_chars, k=username_length))
    return username.lower()+get_domain()


def get_token(payload):
    try:
        response = requests.post(f"{base_url}/token", json=payload)
    except Exception as e:
        print(e)
    return response.json()['token']

def create_email():
    try:
        email = generate_random_email()
        password = generate_password()
        payload = {
    "address": email,
    "password": password
        }
        response = requests.post(f"{base_url}/accounts", json=payload)


        while response.status_code == 429:
            print('wait')
            time.sleep(5)
            response = requests.post(f"{base_url}/accounts", json=payload)

        data = {
    "address": response.json()['address'],
    "password": password
        }
        return data
    except Exception as e:
        print(e)


def extract_code(string):
    code = ""
    for x in string:
        if x.isdigit():
            code += x
    return code


def get_messages(payload):
    for x in range(5):
        try:
            token = {"Authorization":f"Bearer {get_token(payload)}"}
            response = requests.get(f"{base_url}/messages", headers=token)
            codestring = response.json()['hydra:member'][0]['subject']
            code = extract_code(codestring)
            return code
        except Exception:
            time.sleep(3)
    return ""
