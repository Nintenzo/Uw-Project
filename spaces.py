import requests
import os
from dotenv import load_dotenv
from services.db_service import insert_space
from settings.spaces_keywords import subreddits
load_dotenv()
key = os.getenv("CIRCLE_API")
headers = {'Authorization': f'Token {key}'}
community_id = "337793"

def delete_spaces():
    url = f"https://app.circle.so/api/v1/spaces?community_id={community_id}&sort=active&per_page=25"
    response = requests.get(url,headers=headers)
    response = response.json()
    for x , y in enumerate(response):
        url = f"https://app.circle.so/api/v1/spaces/{response[x].get('id')}/"
        data = requests.delete(url,headers=headers)
        print(data.json())

def create_spaces():
    for x in subreddits:
        keywords = ""
        original = ""
        context = ""
        for y in range(0,10):
            original = subreddits.get(x).get('original')
            context = subreddits.get(x).get("context")
            if y == 9:
                keywords += f"{subreddits.get(x).get('keywords')[y]}"
            else:
                keywords += f"{subreddits.get(x).get('keywords')[y]}, "
        url = f"https://app.circle.so/api/v1/spaces?community_id={community_id}&name={x}"
        response = requests.post(url,headers=headers)
        data = response.json()
        id = data.get("space").get("id")
        insert_space(space_name=x, original=original, space_id=id, keywords=keywords,context=context)

create_spaces()