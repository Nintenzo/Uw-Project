import requests
from dotenv import load_dotenv
import os
load_dotenv()
CIRCLE_KEY = os.getenv("CIRCLE_API")
HEADERS = {
'Authorization': f'Token {CIRCLE_KEY}'
}

API_KEY = "ceLDhha7NKK6QMY2LU79B6EPc7LuUfr"
BASE_URL = "https://app.circle.so/api/v1"
COMMUNITY_ID = 337793
PROTECTED_EMAIL = "drmario@globalmedicalinnovations.com"
SPACE_LIST = [1996258, 1996259, 1996260, 1996261, 1996262, 1996263, 1996264, 1996265, 1996266, 1996267, 1996268, 1996269, 1996270, 1996271, 1996272, 1996273, 1996274, 1996275, 1996276, 1996277]
def get_all_members():
	page = 1
	emails = []
	while True:    
		url = f"{BASE_URL}/community_members?sort=latest&per_page=100&page={page}"
		response = requests.get(url, headers=HEADERS)
		
		if response.status_code != 200:
			print(f"Error fetching page {page}: {response.status_code}")
			break

		data = response.json()
		print(data)
		if not data:
			break

		members = data if isinstance(data, list) else data.get("community_members", [])
		if not members:
			break

		for member in members:
			email = member.get("email")
			if email:
				emails.append(email)

		page += 1

	return emails

def delete_member(email):
	url = f"{BASE_URL}/community_members?community_id={COMMUNITY_ID}&email={email}"
	headers = {'Authorization': 'Token ceLDhha7NKK6QMY2LU79B6EPc7LuUfrz'}

	response = requests.delete(url, headers=HEADERS)
	if response.status_code == 200:
		print(f"✅ Deleted: {email}")
	else:
		print(f"❌ Failed to delete {email}: {response.status_code} - {response.text}")

def start_delete_memebers():
	emails = get_all_members()
	print(f"Found {len(emails)} members.")

	for email in emails:
		if email.lower() == PROTECTED_EMAIL.lower():
			print(f"🔒 Skipping protected email: {email}")
			continue
		delete_member(email)


def start_delete_posts(community_id, space_id):
	for x in space_id:
		url = f"https://app.circle.so/api/v1/posts?community_id={community_id}&space_id={x}"
		response = requests.get(url,headers=HEADERS)
		data = response.json()
		for x in data:
			response = requests.delete(f"https://app.circle.so/api/v1/posts/{x['id']}?community_id={community_id}", headers=HEADERS)
			print(response.json())

start_delete_posts(COMMUNITY_ID, SPACE_LIST)