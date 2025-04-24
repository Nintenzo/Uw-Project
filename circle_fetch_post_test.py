from dotenv import load_dotenv
import os
import requests
load_dotenv()

circle_key = os.getenv("CIRCLE_API")
circle_headers = {
    'Authorization': f'Token {circle_key}'
}

post_id = "20907163"
community_id = os.getenv("COMMUNITY_ID")

circle_post = f"https://app.circle.so/api/v1/posts/{post_id}?community_id={community_id}"
r = requests.get(circle_post, headers=circle_headers)
print(r.json())
print("\n", r.json()['body']['body'])
print("\n", r.json()['name'])