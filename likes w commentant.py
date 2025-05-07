from services.db_service import fetch_posts, get_random_user_email, decrement_likes_comments, fetch_post_byID
from services.until4am import sleep_until_4am
from services.circle_services import like_post, comment_on_post
import random
import time
from datetime import datetime

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

def like_comment_sum(posts):
    total_likes = 0
    total_comments = 0
    for post in posts:
        total_likes += post[8]
        total_comments += post[9]
    total_interactions = total_likes + total_comments
    hour = (sleep_until_4am() / 60 / 60 )
    total_time_seconds = hour * 60 * 60
    average_sleep_time = total_time_seconds // total_interactions
    percentage = random.uniform(-0.3, 0.3)
    average_sleep_time = int(average_sleep_time * (1 + percentage))
    return average_sleep_time

while True:
    try:
        posts = fetch_posts()
        previous_openings = []
        if len(posts) >= 1:
            average_sleep_time = like_comment_sum(posts)
            for x in posts:
                print(average_sleep_time)
                email = get_random_user_email()
                print('emailed changed')
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
                    comment_body = comment_on_post(space_id, post_id, email, previous_openings=previous_openings)
                    if comment_body:
                        opening = extract_opening(comment_body)
                        previous_openings.append(opening)
                    decrement_likes_comments(post_id, "needed_comments")
                    #time.sleep(average_sleep_time)
                    continue
                while needed_comments <= 0 and needed_likes >= 1:
                    print(f"Likes left: {needed_likes}")
                    email = get_random_user_email()
                    response = like_post(post_id, email)
                    while response['message'] != "Post has been liked":
                        email = get_random_user_email()
                        response = like_post(post_id, email)
                    decrement_likes_comments(post_id, "needed_likes")
                    needed_likes = fetch_post_byID(post_id)[8]
        else:
            print(datetime.now())
            #time.sleep(3600)
    except Exception as e:
        print(e)
        time.sleep(120)
        
