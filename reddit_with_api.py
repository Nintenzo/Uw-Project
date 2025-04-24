import time
import praw
import openai
import sqlite3
from settings.spaces_keywords import subreddits
openai.api_key = "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"
count = 0


# def update_post_by_link(link, new_title, new_description, new_posted):
#     global cursor,conn
#     query_update = '''
#         UPDATE posts
#         SET title = ?, description = ?, posted = ?
#         WHERE links = ?;
#     '''
#     cursor.execute(query_update, (new_title, new_description, new_posted, link))
#     conn.commit()
#     print('updated')
#     return


def scrap_reddit():
    reddit = praw.Reddit(
        client_id='eO2afxALnHOM8kvjP0QhxA',
        client_secret='tqLAHXpB4rfsRnsyV6WVtrxcp9MK2g',
        user_agent='my_reddit_scraper_by_u/Ninntendo_Kid33'
    )

    return reddit

# def get_posts():
#     global cursor, conn
#     cursor.execute("""SELECT * FROM posts 
#                    WHERE posted = False
#                    ORDER BY RANDOM() LIMIT 1""")  # Select all columns from the posts table
#     rows = cursor.fetchall()  # Fetch all rows from the query
#     id = rows[0][1]
#     title = rows[0][2]
#     description = rows[0][3]
#     posted = True
#     update_post_by_link(id,title,description,posted)
    

def main():
    global count
    reddit = scrap_reddit()


    for sub in subreddits:
        original = subreddits.get(sub).get('original')
        print(f"Space Category = {sub}")
        print(f"Original Subreddit = {original}")
        subbredit = reddit.subreddit(original)
        for y in range(0,10):
            key = subreddits.get(sub).get('keywords')[y]
            print(key)
            time.sleep(2)
            for post in subbredit.search(key, limit=10):
                id = post.permalink
                # cursor.execute("SELECT links FROM posts")
                # links = [row[0] for row in cursor.fetchall()]  
                # if id in links:
                #     print('pass')
                #     continue
                # else:
                #     links.append(id)
                #     cursor.execute("INSERT INTO posts (links) VALUES (?)", (id,))
                #     conn.commit()
                if post.author == 'AutoModerator':
                    continue
                title = post.title
                description = post.selftext
                print(title)
                print(description)
                time.sleep(555555)
                url = f"https://www.reddit.com{id}"
                print(id)
                print(count)
                count += 1
#               count +=1
#               message = f"""
# I will send you a Reddit post. I want you to rewrite it in a different format to avoid plagiarism. 
# Only return the rewritten version with the **title on the first line**, and the **description** following it. 
# Do not include labels like 'Title:' or 'Description:'. Just the rewritten content.
# Title: {title}
# Description: {description}
# """         
#                 title, description = send_to_gpt(message)
#                 title = title
#                 description = description
#                 posted = False
#                 update_post_by_link(id,title,description,posted)
#                 time.sleep(15)


main()