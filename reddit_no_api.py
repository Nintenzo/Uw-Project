import time
import praw
import openai
import sqlite3
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from seleniumbase import Driver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC




def create_driver():
    global driver,wait
    data = r"C:\Users\mahme\AppData\Local\Google\Chrome\User Data"
    driver = Driver(uc=True, user_data_dir=data,headed=False)
    driver.set_window_position(-10000, 0)  # Move the browser window off-screen to avoid UI interference (no headless support)
    wait = WebDriverWait(driver, 30)

create_driver()

def is_typing(driver):
    try:
        #Replace this with the actual typing indicator if needed
        element = driver.find_element(By.ID, "composer-submit-button")
        return element.is_displayed()
    except Exception:
        return False
    

def safe_send_multiline(text):
 for line in text.splitlines():
    element.send_keys(line)
    element.send_keys(Keys.SHIFT, Keys.ENTER)


conn = sqlite3.connect("reddit_scrap.db")
cursor = conn.execute("""
CREATE TABLE IF NOT EXISTS posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    links TEXT NOT NULL
)
""")

count = 0

reddit = praw.Reddit(
    client_id='eO2afxALnHOM8kvjP0QhxA',
    client_secret='tqLAHXpB4rfsRnsyV6WVtrxcp9MK2g',
    user_agent='my_reddit_scraper_by_u/Ninntendo_Kid33'
)

subreddits = [reddit.subreddit('lostarkgame'),reddit.subreddit('upwork'),]

count = 0

for subreddit in subreddits:
    for post in subreddit.new(limit=None):
        cursor.execute("SELECT links FROM posts")
        links = [row[0] for row in cursor.fetchall()]  
        if post.permalink in links:
            print('pass')
            continue
        else:
            links.append(post.permalink)
            print(post.permalink)
            cursor.execute("INSERT INTO posts (links) VALUES (?)", (post.permalink,))
            conn.commit()
            # Skip posts made by AutoModerator or with titles matching specific keywords
            if post.author == 'AutoModerator':
                continue  # Skip this post and move to the next one
            title = post.title
            description = post.selftext

            url = f"https://www.reddit.com{post.permalink}"
            print(url)
            print(count)
            count +=1
            print("=========================================================================")
            # Format the message to send to GPT
            message = f"I will send you a post now I want you to rewrite aka palagarism it in a different format with nothing else in your message just the title and the description. Make the title in the first line of your message, don't include the word title and description before."
            title = f"Title: {title}"
            description = f"Description: {description}"
            driver.get("https://chatgpt.com/")
            button = wait.until(EC.visibility_of_any_elements_located((By.CSS_SELECTOR, 'button[aria-label="New chat"]')))[0]
            button.click()
            try:
                wait = WebDriverWait(driver, 2)
                danger = wait.until(EC.visibility_of_any_elements_located((By.CLASS_NAME,"btn relative btn-danger btn-giant mb-3")))[0]
                danger.click()
            except Exception:
                pass
            wait = WebDriverWait(driver, 30)
            element = wait.until(EC.visibility_of_all_elements_located((By.CLASS_NAME,"ProseMirror")))[0]
            safe_send_multiline(message)
            element.send_keys(Keys.SHIFT, Keys.ENTER)
            safe_send_multiline(title)
            element.send_keys(Keys.SHIFT, Keys.ENTER)
            safe_send_multiline(description)
            element.send_keys(Keys.ENTER)
            element = wait.until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, ".flex.w-full.flex-col.gap-1.empty\\:hidden.first\\:pt-\\[3px\\]")))[0]
            time.sleep(0.5)
            while is_typing(driver):
                print("still typing...")
                time.sleep(1)
            element = wait.until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, ".flex.w-full.flex-col.gap-1.empty\\:hidden.first\\:pt-\\[3px\\]")))[0]
            print("REDDIT TEXT")
            print("----------------------------------------------------")
            print(title)
            print(description)
            print("----------------------------------------------------")
            print("CHAT GPT TEXT")
            print("----------------------------------------------------")
            print(element.text)
            print("----------------------------------------------------")

            driver.quit()
            create_driver()

    # retry = document.getElementsByClassName("btn relative btn-secondary")[1].textContent