import requests
import cloudscraper
import time
url = "https://login.circle.so/sign_in?"

scraper = cloudscraper.create_scraper()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive"
}

payload = {
    "community_id": "",
    "email": "ixpyye6556@atminmail.com",
    "password": "OL>,`pAO=/22"
}

response = scraper.post(url, data=payload,headers=headers) # cloudflare is blocking the request 
print(response.cookies)
print(response.status_code)
with open("html.txt","w") as file:
    file.write(response.text)