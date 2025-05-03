from services.circle_services import create_post
from services.db_service import get_random_user_email, create_post_db, check_if_posted
from datetime import datetime, timedelta
import schedule
import time
import os
import praw
import random
from dotenv import load_dotenv
from get_reddits import get_subs
from settings.spaces_keywords import subreddits as all_subreddits
load_dotenv()

count = 0
max_post = 18

def setup_scrapper():
     reddit = praw.Reddit(
         client_id= os.getenv('CLIENT_ID'),
         client_secret= os.getenv('CLIENT_SECRET'),
         user_agent= os.getenv('USER_AGENT'),
     )
 
     return reddit


def main():
    global count
    scraped = 0
    reddit = setup_scrapper()
    conn, cursor = create_post_db()
    subs_post_plan, avg_sleep_time = get_subs()
    print(f"Subreddits to scrape: {subs_post_plan}")
    for sub_key, num_posts in subs_post_plan.items():
        if sub_key not in all_subreddits:
            print(f"Skipping {sub_key} - not found in all_subreddits.")
            continue
        sub_data = all_subreddits[sub_key]
        original_subreddit_name = sub_data.get('original')
        space_id = sub_data.get('space_id', 9999)
        keywords = sub_data.get('keywords', [])
        if not original_subreddit_name:
            print(f"Skipping {sub_key} - missing 'original' subreddit name.")
            continue
        for _ in range(num_posts):
            if scraped >= max_post:
                break
            try:
                subreddit = reddit.subreddit(original_subreddit_name)
                if not keywords:
                    print("No keywords found.")
                else:
                    keyword = random.choice(keywords)
                    print(f"Searching keyword: {keyword}")
                    for post in subreddit.search(keyword, sort=random.choice(["new", "relevance"])):
                        reddit_link = post.permalink
                        original_title = post.title
                        original_description = post.selftext
                        author = post.author.name if post.author else "[deleted]"
                        post_info = f"-- Found Post: {original_title}"
                        print(f"{post_info}")
                        print(f"Link: {reddit_link}")
                        if author == 'AutoModerator':
                            print("Skipping AutoModerator post.")
                            continue
                        if check_if_posted(reddit_link, cursor):
                            print("Skipping: Already posted.")
                            continue
                        print("Processing: Post is new.")
                        try:
                            random_email = get_random_user_email()
                            if not random_email:
                                print("Error: Could not fetch random email. Skipping post.")
                                continue
                            print(f"Processing and Posting to Circle using email: {random_email}...")
                            status = create_post(
                                space_id = space_id,
                                email = random_email,
                                title = original_title,
                                description = original_description,
                                url = reddit_link
                            )
                            if status == "false":
                                continue
                        except Exception as e:
                            print(f"Error during Circle processing/posting: {e}")
                        print("--- Done with this keyword ---")
                        sleep_time = random.randint(avg_sleep_time - 900, avg_sleep_time + 250)
                        print(sleep_time)
                        time.sleep(sleep_time)
                        break
            except praw.exceptions.PRAWException as e:
                print(f"Error accessing subreddit {original_subreddit_name}: {e}")
            except Exception as e:
                err_msg = (
                    f"An unexpected error occurred for {original_subreddit_name}"
                )
                print(f"{err_msg}: {e}")
    print(f"Finished processing. Total new posts logged: {count}")
    if conn:
        conn.close()


def sleep_until_4am():
    now = datetime.now()
    today_4am = now.replace(hour=4, minute=0, second=0, microsecond=0)

    if now > today_4am:
        target = today_4am + timedelta(days=1)
    else:
        target = today_4am

    sleep_seconds = (target - now).total_seconds()
    if sleep_seconds > 0:
        print(f"Current time is {now}. Sleeping for {sleep_seconds} seconds until {target}...")
        time.sleep(sleep_seconds)
        time.sleep(10)
    else:
        print(f"Current time is {now}. It's already past 04:00, starting schedule immediately.")

schedule.every().day.at("04:00").do(main)
main()
while True:
    schedule.run_pending()
    sleep_until_4am()
