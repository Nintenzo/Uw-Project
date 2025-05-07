import requests
import random
import json
from settings.pinterest_keywords import pinterest_keywords

def get_img(name, gender, add, og):
    key = random.choices([random.choice(pinterest_keywords), name], [0.6, 0.4])[0]
    if add:
        search = f"{key} {gender}"
    else:
        search = f"{key} {og}"

    headers = {
        "x-csrftoken": "mowa"
    }
    cookies = {
        "csrftoken": "mowa"

    }
    url = f"https://www.pinterest.com/resource/BaseSearchResource/get/?source_url=/search/pins/?q={search}"
    payload = {
        "options": {
            "query": search,
            "page_size": 25,
            "scope": "pins"
        },
        "context": {}
    }
    try:
        response = requests.post(
            url,
            data={"data": json.dumps(payload)},
            headers=headers,
            cookies=cookies,
            timeout=5
        )
    except Exception:
        print('Pinterest Timeout Error')
        return "", search
    img = response.json()
    img_list = []
    if img["resource_response"]["data"]["results"]:
        for x in img["resource_response"]["data"]["results"]:
            img_list.append(x["images"]["474x"]["url"])
            if len(img_list) >= 10:
                break
        img = random.choice(img_list)
    else:
        return "", search
    return img, search
