from settings.spaces_keywords import subreddits
import random

def get_subs():
    desired_posts = random.randint(1,8)
    print(desired_posts)
    subs = {}
    subs_list = []
    high_traffic = [name for name, data in subreddits.items() if data["traffic"] == "high"]
    mid_traffic = [name for name, data in subreddits.items() if data["traffic"] == "mid"]
    low_traffic = [name for name, data in subreddits.items() if data["traffic"] == "low"]
    subs_list.extend(random.choices(high_traffic,k=random.randint(1,2)))
    mid = random.choices([True,False],[0.4,0.6])
    low = random.choices([True,False],[0.2,0.8])
    high = "False"
    while len(subs) < desired_posts:
        if str(high[0]) == "True":
            subs_list.extend(random.choices(mid_traffic,k=random.randint(1,2)))
        if str(mid[0]) == "True":
            subs_list.extend(random.choices(mid_traffic,k=random.randint(1,2)))
        if str(low[0]) == "True":
            subs_list.extend(random.choices(low_traffic,k=random.randint(1,2)))
        for x in subs_list:
            subs[x] = subreddits.get(x)
        high = random.choices([True,False],[0.6,0.4])
        mid = random.choices([True,False],[0.4,0.6])
        low = random.choices([True,False],[0.2,0.8])
    return subs
