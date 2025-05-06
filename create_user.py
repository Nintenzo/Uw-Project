import os
from dotenv import load_dotenv
import requests
from activator_service import send_otp
from services.password_service import generate_password
load_dotenv()
url = "https://app.circle.so/api/v1/community_members"

community_id = os.getenv("COMMUNITY_ID")
email = "qfdbwvrcmnxgnvcqpx@hthlm.com"
password = generate_password()
payload = {
        "email": email,
        "password": password,
        "name": 'ds',
        "headline": 'sd',
        "bio": 'sd',
        "avatar": "https://i.pinimg.com/474x/58/fa/4f/58fa4f2a21757e0314b4e2556e9c9072.jpg",
        "community_id": community_id,
    }

headers = {'Authorization': 'Token ceLDhha7NKK6QMY2LU79B6EPc7LuUfrz'}
response = requests.request("POST", url, headers=headers, json=payload)
print(email)
print(password)
send_otp(email, password)
