from services.circle_services import create_post
from services.db_service import get_random_user_email, create_post_db, check_if_posted, get_random_user_email
from datetime import datetime, timedelta
import schedule
import time
import praw
import random
from dotenv import load_dotenv
from get_reddits import get_subs
load_dotenv()

count = 0
max_post = 18

def setup_scrapper():
    reddit = praw.Reddit(
        client_id='eO2afxALnHOM8kvjP0QhxA',
        client_secret='tqLAHXpB4rfsRnsyV6WVtrxcp9MK2g',
        user_agent='my_reddit_scraper_by_u/Ninntendo_Kid33'
    )
    return reddit


def main():
    global count
    scraped = 0
    reddit = setup_scrapper()
    conn, cursor = create_post_db()
    subreddits = get_subs()
    for sub_key, sub_data in subreddits.items():
        if scraped >= max_post:
            break
        original_subreddit_name = sub_data.get('original')
        space_id = sub_data.get('space_id', 9999)
        # print(f"Space ID = {space_id}")
        # print(f"Space Category = {sub_key}")
        # print(f"Original Subreddit = {original_subreddit_name}")
        if not original_subreddit_name:
            print(f"Skipping {sub_key} - missing 'original' subreddit name.")
            continue

        try:
            subreddit = reddit.subreddit(original_subreddit_name)
            keywords = sub_data.get('keywords', [])
            if not keywords:
                print("No keywords found.")
            else:
                keyword = random.choice(keywords)
                print(f"Searching keyword: {keyword}")
                print(keyword)
                
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
                        create_post(
                            space_id = space_id,
                            email = random_email,
                            title = original_title,
                            description = original_description,
                            url = reddit_link
                        )

                    except Exception as e:
                        print(f"Error during Circle processing/posting: {e}")

                    print("--- Done with this keyword ---")
                    sleep = random.randint(1200,5400)
                    time.sleep(sleep)
                    scraped += 1
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
    # Get today's 04:00
    today_4am = now.replace(hour=4, minute=0, second=0, microsecond=0)
    
    # If current time is past 04:00, set target to tomorrow's 04:00
    if now > today_4am:
        target = today_4am + timedelta(days=1)
    else:
        target = today_4am
    
    # Calculate seconds to sleep
    sleep_seconds = (target - now).total_seconds()
    if sleep_seconds > 0:
        print(f"Current time is {now}. Sleeping for {sleep_seconds} seconds until {target}...")
        time.sleep(sleep_seconds)
        time.sleep(10)
    else:
        print(f"Current time is {now}. It's already past 04:00, starting schedule immediately.")

main()
schedule.every().day.at("04:00").do(main)

while True:
    schedule.run_pending()
    sleep_until_4am()

