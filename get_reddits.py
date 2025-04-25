from settings.spaces_keywords import subreddits
from services.db_service import get_users_count
import random


def get_subs():
    users = get_users_count()
    # Calculate daily post target (8–15 posts per day)
    daily_posts = max(8, min(15, users // 800))

    variation = random.choice([-3, -2, -1, 0, 1, 2, 3])
    daily_posts = max(6, min(15, daily_posts + variation))

    # Categorize subreddits by traffic
    high_traffic = [name for name, data in subreddits.items() if data["traffic"] == "high"]
    mid_traffic = [name for name, data in subreddits.items() if data["traffic"] == "mid"]
    low_traffic = [name for name, data in subreddits.items() if data["traffic"] == "low"]

    # Assign base frequencies
    post_plan = {}
    # High-traffic: 1–2 posts per day
    for sub in high_traffic:
        post_plan[sub] = random.randint(1, 2)
    # Mid-traffic: 1 post every 2–3 days (~0.4 posts/day)
    for sub in mid_traffic:
        post_plan[sub] = 1 if random.random() < 0.4 else 0
    # Low-traffic: 1 post every 4–5 days (~0.22 posts/day)
    for sub in low_traffic:
        post_plan[sub] = 1 if random.random() < 0.22 else 0

    total = sum(post_plan.values())
    # If too many, reduce from low/mid first
    if total > daily_posts:
        for tier in [low_traffic, mid_traffic, high_traffic]:
            for sub in random.sample(tier, len(tier)):
                if post_plan[sub] > 0 and total > daily_posts:
                    post_plan[sub] -= 1
                    total -= 1

    # If too few, add to high/mid first
    elif total < daily_posts:
        for tier in [high_traffic, mid_traffic, low_traffic]:
            for sub in random.sample(tier, len(tier)):
                if total < daily_posts:
                    post_plan[sub] += 1
                    total += 1

    post_plan = {k: v for k, v in post_plan.items() if v > 0}
    return post_plan
