from services.circle_services import create_post
from settings.spaces_keywords import subreddits
from services.db_service import create_post_db, check_if_posted, get_random_user_email
import time
import praw
from dotenv import load_dotenv
load_dotenv()

count = 0


def setup_scrapper():
    reddit = praw.Reddit(
        client_id='eO2afxALnHOM8kvjP0QhxA',
        client_secret='tqLAHXpB4rfsRnsyV6WVtrxcp9MK2g',
        user_agent='my_reddit_scraper_by_u/Ninntendo_Kid33'
    )
    return reddit


def main():
    global count
    reddit = setup_scrapper()
    conn, cursor = create_post_db()

    for sub_key, sub_data in subreddits.items():
        original_subreddit_name = sub_data.get('original')
        space_id = sub_data.get('space_id', 9999)
        print(f"Space ID = {space_id}")
        print(f"Space Category = {sub_key}")
        print(f"Original Subreddit = {original_subreddit_name}")
        if not original_subreddit_name:
            print(f"Skipping {sub_key} - missing 'original' subreddit name.")
            continue

        try:
            subreddit = reddit.subreddit(original_subreddit_name)
            keywords = sub_data.get('keywords', [])
            for keyword in keywords:
                print(f"Searching keyword: {keyword}")
                for post in subreddit.search(keyword):
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
                        # Fetch a random email first
                        random_email = get_random_user_email()
                        if not random_email:
                            print("Error: Could not fetch random email. Skipping post.")
                            continue
                        print(f"Processing and Posting to Circle using email: {random_email}...")
                        create_post(
                            space_id=space_id,
                            original_title=original_title,
                            original_description=original_description,
                            url=reddit_link,
                            email=random_email
                        )
                    except Exception as e:
                        print(f"Error during Circle processing/posting: {e}")

                    print("--- Done with post ---")
                    time.sleep(5)

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


main()
