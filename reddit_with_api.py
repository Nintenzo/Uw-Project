import time
import praw
import openai
import sqlite3
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from seleniumbase import Driver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

openai.api_key = "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"
count = 0
conn = sqlite3.connect("reddit_scrap.db")
cursor = conn.cursor()
def send_to_gpt(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an expert rewriter that transforms text to avoid plagiarism "
                    "while keeping the meaning intact. You only return clean, reformatted content without extra commentary."
                ),
            },
            {"role": "user", "content": prompt}
        ]
    )
    rewrite = response["choices"][0]["message"]["content"]
    title = rewrite.split('\n')[0]
    description = rewrite.split('\n')[1:]
    return title, description

def create_db():
    global cursor, conn
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        links TEXT NOT NULL,
        title TEXT,
        description TEXT,
        posted BOOL DEFAULT False
    )
    """)
    return

def update_post_by_link(link, new_title, new_description, new_posted):
    global cursor,conn
    query_update = '''
        UPDATE posts
        SET title = ?, description = ?, posted = ?
        WHERE links = ?;
    '''
    cursor.execute(query_update, (new_title, new_description, new_posted, link))
    conn.commit()
    print('updated')
    return


def scrap_reddit():
    reddit = praw.Reddit(
        client_id='eO2afxALnHOM8kvjP0QhxA',
        client_secret='tqLAHXpB4rfsRnsyV6WVtrxcp9MK2g',
        user_agent='my_reddit_scraper_by_u/Ninntendo_Kid33'
    )

    subnames = ['lostarkgame', 'upwork']
    subreddits = [reddit.subreddit(name) for name in subnames]
    return subreddits

def get_posts():
    global cursor, conn
    cursor.execute("""SELECT * FROM posts 
                   WHERE posted = False
                   ORDER BY RANDOM() LIMIT 1""")  # Select all columns from the posts table
    rows = cursor.fetchall()  # Fetch all rows from the query
    id = rows[0][1]
    title = rows[0][2]
    description = rows[0][3]
    posted = True
    update_post_by_link(id,title,description,posted)
    

def main():
    global count
    create_db()
    for subreddit in scrap_reddit():
        for post in subreddit.top(limit=10, time_filter='day'):
            id = post.permalink
            cursor.execute("SELECT links FROM posts")
            links = [row[0] for row in cursor.fetchall()]  
            if id in links:
                print('pass')
                continue
            else:
                links.append(id)
                cursor.execute("INSERT INTO posts (links) VALUES (?)", (id,))
                conn.commit()
                if post.author == 'AutoModerator':
                    continue
                title = post.title
                description = post.selftext
                #UNIMPORTANT####
                url = f"https://www.reddit.com{id}"
                print(id)
                print(count)
                count +=1
                ################
                message = f"""
I will send you a Reddit post. I want you to rewrite it in a different format to avoid plagiarism. 
Only return the rewritten version with the **title on the first line**, and the **description** following it. 
Do not include labels like 'Title:' or 'Description:'. Just the rewritten content.
Title: {title}
Description: {description}
"""         
                title, description = send_to_gpt(message)
                title = title
                description = description
                posted = False
                update_post_by_link(id,title,description,posted)
                time.sleep(15)


main()
