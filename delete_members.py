import requests

API_KEY = "ceLDhha7NKK6QMY2LU79B6EPc7LuUfr"
BASE_URL = "https://app.circle.so/api/v1"

COMMUNITY_ID = 337793
PROTECTED_EMAIL = "drmario@globalmedicalinnovations.com"

def get_all_members():
	page = 1
	emails = []
	while True:
		headers = {'Authorization': 'Token ceLDhha7NKK6QMY2LU79B6EPc7LuUfrz'}
    
		url = f"{BASE_URL}/community_members?sort=latest&per_page=100&page={page}"
		response = requests.get(url, headers=headers)
		
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

	response = requests.delete(url, headers=headers)
	if response.status_code == 200:
		print(f"✅ Deleted: {email}")
	else:
		print(f"❌ Failed to delete {email}: {response.status_code} - {response.text}")

def main():
	emails = get_all_members()
	print(f"Found {len(emails)} members.")

	for email in emails:
		if email.lower() == PROTECTED_EMAIL.lower():
			print(f"🔒 Skipping protected email: {email}")
			continue
		delete_member(email)

if __name__ == "__main__":
	main()
