import requests
from bs4 import BeautifulSoup
import time
import random
import string
import cloudscraper
from PIL import Image
from imgurpython import ImgurClient
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from seleniumbase import Driver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import subprocess
import re
import os
from selenium.webdriver.common.by import By
import sqlite3

scraper = cloudscraper.create_scraper()
url = "https://app.circle.so/api/v1/community_members"
conn = sqlite3.connect("circle_users.db")
cursor = conn.cursor()

def restart_warp():
    subprocess.run(["warp-cli", "disconnect"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.run(["warp-cli", "connect"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)   
    result = subprocess.run(["warp-cli", "status"], capture_output=True, text=True)
    output = result.stdout.strip()
    while output != "Status update: Connected":
        result = subprocess.run(["warp-cli", "status"], capture_output=True, text=True)
        output = result.stdout.strip()
        time.sleep(1)
    return

def create_driver():
    global driver
    driver = Driver(uc=True, incognito=True, headless=False)
    return driver

def create_db():
    global cursor, conn
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,        
        email TEXT NOT NULL,
        password TEXT,
        bio TEXT,
        headline TEXT,
        avatar TEXT
    )
    """)
    return

def generate_password(length=12):
    if length < 4:
        raise ValueError("Password length should be at least 4")
    password_chars = [
        random.choice(string.ascii_lowercase),
        random.choice(string.ascii_uppercase),
        random.choice(string.digits),
        random.choice(string.punctuation),
    ]
    all_chars = string.ascii_letters + string.digits + string.punctuation
    password_chars += random.choices(all_chars, k=length - len(password_chars))
    random.shuffle(password_chars)
    return ''.join(password_chars)

def imgur_uploader(image_url):
    if not os.path.exists("persons"):
        os.makedirs("persons")
    image_filename = image_url.split("/")[-1]
    image_path = os.path.join("persons", image_filename)
    with open(image_path, 'wb') as f:
        f.write(scraper.get(image_url).content)

    client = ImgurClient('b4c533826633a63', 'dffc6142394eed90f22960d0c9c25a8d85cdbe86')
    uploaded_image = client.upload_from_path(image_path, config=None, anon=True)
    imgur_url = uploaded_image['link']
    return imgur_url

def pinterest():
    try:
        categories = [
            "anime", "cartoon", "pixel art", "manga", "webtoon", "chibi",
            "movie", "tv series", "netflix", "hbo", "sitcom", "disney",
            "marvel", "dc", "star wars", "harry potter", "ghibli", "pixar",
            "kdrama", "reality tv", "celebrity", "influencer", "streamer",
            "gamer", "cosplayer", "vtuber", "irl selfie", "candid photo",
            "portrait", "headshot", "selfie", "mugshot", "photobooth", "passport photo",
            "emo", "goth", "scene", "e-girl", "e-boy", "vsco girl",
            "alt", "grunge", "soft grunge", "dark academia", "light academia",
            "y2k", "cybercore", "dreamcore", "weirdcore", "corecore", "mallgoth",
            "retro", "vintage", "old photo", "blurry", "low quality", "high quality",
            "aesthetic", "funny", "random", "meme", "reaction", "sad", "cute", "cool",
            "artsy", "3D render", "AI art", "doodle", "sketch", "painting",
            "lofi", "nostalgic", "moody", "emotional", "dramatic", "chill",
            "fashion", "streetwear", "minimalist", "bold", "cozy", "chaotic",
            "kpop", "jpop", "idol", "fanart", "screenshot", "cinematic"
        ]

        modifiers = [
            "pfp", "profile picture", "avatar", "icon", "display picture",
            "aesthetic pfp", "anime pfp", "realistic pfp", "headshot icon",
            "reaction pfp", "cartoon icon", "face pic", "portrait shot",
            "cool pfp", "funny avatar", "moody pfp", "soft pfp", "stylish pfp",
            "anime boy icon", "anime girl pfp", "irl profile pic"
        ]

        pinterest_keywords = [f"{cat} {mod}" for cat in categories for mod in modifiers]
        driver = create_driver()
        wait = WebDriverWait(driver, 60)
        key = random.choice(pinterest_keywords)
        print(key)
        print(f"Searching Pinterest for: {key}")
        driver.get(f"https://www.pinterest.com/search/pins/?q={key}")
        for _ in range(1):
            time.sleep(1.5)
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        image_urls = []
        for _ in range(10):
            try:
                images_containers = driver.find_elements(By.CSS_SELECTOR, ".Yl-.MIw.Hb7")
                numbers = []
                for x in range(0, len(images_containers)):
                    numbers.append(x)
                for x in numbers:
                    if images_containers:
                        n = random.choice(numbers)
                        numbers.remove(n)
                        images = images_containers[n].find_elements(By.TAG_NAME, "img")
                        image_urls.extend([img.get_attribute("src") for img in images if img.get_attribute("src")])
                    else:
                        print("No image containers found.")
            except Exception as e:
                print(f"Error while fetching images: {e}")

        image_urls = list(set(image_urls))
        img = random.choice(image_urls)
        driver.quit()
        return img
    except Exception:
        driver.quit()
        time.sleep(1)
        pinterest()

def get_next_sibling_text(label_text,soup):
    label = soup.find(string=label_text)
    if label:
        return label.find_next().get_text(strip=True)
    else:
        return "Label not found."
    
def scrap_person_data():
	try:
		# Setup
		url = "https://www.fakepersongenerator.com/Index/generate"
		response = scraper.get(url)
		soup = BeautifulSoup(response.text, "html.parser")
          
		# Name
		full_name = soup.select_one('.click').text.replace("\xa0", " ")

		# Avatar image
		image_srcs = [tag['src'] for tag in soup.find_all(src=lambda s: s and s.startswith('/Face'))]
		avatar_url = f"https://www.fakepersongenerator.com{image_srcs[0]}" if image_srcs else None

		# Headline (Job Title)
		job_title_input = None
		job_label = soup.find("span", string=lambda t: t and t.strip() == "Occupation(Job Title)")
		if job_label:
			info_div = job_label.find_parent("div", class_="info-title")
			next_div = info_div.find_next_sibling() if info_div else None
			job_title_input = next_div.find("input")["value"] if next_div and next_div.find("input") else ""

		# Bio options
		bio_labels = ["Online Status", "Online Signature", "Online Biography"]
		bios = [get_next_sibling_text(label, soup) for label in bio_labels if get_next_sibling_text(label, soup)]
		selected_bio = random.choice(bios) if bios else ""

		# Gender and city
		gender = city = ""
		details_div = soup.find("div", class_="col-md-8 col-sm-6 col-xs-12")
		if details_div:
			text = details_div.get_text(separator=" ", strip=True)
			if "Gender:" in text:
				gender = text.split("Gender:")[1].split()[0].strip()
			if "City, State, Zip:" in text:
				city = text.split("City, State, Zip:")[1].split(",")[0].strip()

		# Username
		username = get_next_sibling_text("Username", soup)
          
		name = [full_name, username]

		# Select final image
		pin_img = pinterest()
		image_url = random.choice([avatar_url, pin_img])
		imgur_url = imgur_uploader(image_url)
		# Return all data
		return name, gender, selected_bio, job_title_input, city, imgur_url

	except Exception as e:
		print("Error:", e)
		restart_warp()

    
def insert_users(name, email, password, bio, headline, avatar):
    global cursor, conn
    try:
        # Insert data into the posts table
        cursor.execute("""
        INSERT INTO users (name, email, password, bio, headline, avatar)
        VALUES (?, ?, ?, ?, ?, ?)

        """, (name, email, password, bio, headline, avatar))
        conn.commit()
        print("Data inserted successfully!")
    except sqlite3.Error as e:
        print(f"Error inserting data: {e}")
    return


def get_mail(x=None):
    global wait, driver,circle,mail,tabs
    if x == "mail":
        driver = create_driver()
        wait = WebDriverWait(driver, 60)
        driver.get('https://minmail.app/10-minute-mail')
        driver.execute_script("window.open('https://login.circle.so/sign_in?request_host=app.circle.so#email', '_blank');")
        tabs = driver.window_handles
        circle = tabs[1]
        mail = tabs[0]
        driver.switch_to.window(mail)
        email_div = wait.until(EC.visibility_of_element_located((By.XPATH, "//div[contains(@class, 'text-foreground')]")))
        email = email_div.text
        return email
    else:
        codeele = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, '.flex.lg\\:justify-start.text-sm.font-medium.truncate.text-gray-900')))
        code = codeele.text
        reg = re.findall(r'\d+', code)
        return ''.join(reg)

def activate_user(email,pw):
    driver.switch_to.window(circle)
    emailform = wait.until(EC.visibility_of_element_located((By.NAME, "user[email]")))
    emailform.send_keys(email)
    password = wait.until(EC.visibility_of_element_located((By.NAME, "user[password]")))
    password.send_keys(pw)
    password.send_keys(Keys.ENTER)
    driver.switch_to.window(mail)
    code = get_mail()
    driver.switch_to.window(circle)
    otpele = wait.until(EC.visibility_of_element_located((By.NAME, "otp")))
    otpele.send_keys(code)
    submit = wait.until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, 'button[type="submit"]')))
    while submit:
        for btn in submit:
            if btn.text == "Continue":
                btn.click()
                while True:
                    current_url = driver.current_url
                    if current_url == "https://tubiit.circle.so/feed":
                        driver.quit()
                        return
                    time.sleep(0.5)
                    
def create_person():
    payload = {
        "email": mailstring,
        "password": pw,
        "name": fullname,
        "bio": bio,
        "headline": headline,
        "avatar": avatar,
        "community_id": "337793",
        "space_ids": [1987412],
        "skip_invitation": False,
    }
    headers = {
    'Authorization': f'Token ceLDhha7NKK6QMY2LU79B6EPc7LuUfrz'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    print(response.json())
    return

create_db()
while True:
    name,gender,bio,headline,city,avatar = scrap_person_data()
    fullname = random.choice(name)
    mailstring = get_mail(x="mail")
    pw = generate_password()
    create_person()
    activate_user(email=mailstring,pw=pw)
    insert_users(fullname,mailstring, pw, bio, headline, avatar)
