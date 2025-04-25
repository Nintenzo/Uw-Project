from services.db_service import fetch_posts, get_random_user_email, decrement_likes_comments, fetch_post_byID
from services.circle_services import like_post, comment_on_post
from services.seen_service import last_seen
import random
import time
from datetime import datetime, timedelta


def seconds_until_next_430_utc():
    now = datetime.utcnow()
    print(now)
    target = now.replace(hour=4, minute=30, second=0, microsecond=0)

    if now >= target:
        target += timedelta(days=1)

    return (target - now).total_seconds()


def extract_opening(text, num_words=10):
    if not text:
        return ""
    sentence = text.split('.')
    if sentence:
        opening = sentence[0].strip()
        if len(opening.split()) > num_words:
            return ' '.join(opening.split()[:num_words])
        return opening
    return ' '.join(text.split()[:num_words])


while True:
    posts = fetch_posts()
    if len(posts) >= 1:
        for x in posts:
            email = get_random_user_email()
            post_id = x[5]
            space_id = x[6]
            needed_likes = x[8]
            needed_comments = x[9]
            response = like_post(post_id, email)
            while response['message'] != "Post has been liked":
                email = get_random_user_email()
                response = like_post(post_id, email)
            decrement_likes_comments(post_id, "needed_likes")
            if needed_comments >= 1:
                previous_openings = []
                for _ in range(needed_comments):
                    comment_body = comment_on_post(space_id, post_id, email, previous_openings=previous_openings)
                    if comment_body:
                        opening = extract_opening(comment_body)
                        previous_openings.append(opening)
                    decrement_likes_comments(post_id, "needed_comments")
                    if needed_comments < 100:
                        time.sleep(random.randint(225, 525))
                    else:
                        time.sleep(random.randint(120, 210))
                continue
            while needed_comments >= 1 and needed_likes >= 1:
                print(f"Likes left: {needed_likes}")
                email = get_random_user_email()
                response = like_post(post_id, email)
                while response['message'] != "Post has been liked":
                    email = get_random_user_email()
                    response = like_post(post_id, email)
                needed_likes = fetch_post_byID(post_id)[8]
                decrement_likes_comments(post_id, "needed_likes")

    else:       
        #sleep_seconds = seconds_until_next_430_utc()
        #print(f"No posts found. Sleeping until 4:30 AM UTC... ({sleep_seconds:.0f} seconds)")
        #time.sleep(sleep_seconds)
        print(datetime.now())
        time.sleep(3600)
