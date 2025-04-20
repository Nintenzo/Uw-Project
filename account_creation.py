import requests
import re
import time
import random
import cloudscraper
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from seleniumbase import Driver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from services.warp_service import restart_warp
from services.db_service import create_db, insert_users
from services.password_service import generate_password
from services.imgur_service import imgur_uploader
from settings.pinterest_keywords import categories, modifiers

# Helper function for random first letter capitalization
def randomize_first_letter_case(text):
    if not text:
        return ""
    first_char = random.choice([text[0].upper(), text[0].lower()])
    return first_char + text[1:]

scraper = cloudscraper.create_scraper()
url = "https://app.circle.so/api/v1/community_members"


def create_driver():
    global driver
    driver = Driver(uc=True, incognito=True, headless=False)
    return driver


def pinterest():
    try:
        pinterest_keywords = [f"{cat} {mod}" for cat in categories for mod in modifiers]
        driver = create_driver()
        WebDriverWait(driver, 60)
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


def get_next_sibling_text(label_text, soup):
    label = soup.find(string=label_text)
    if label:
        return label.find_next().get_text(strip=True)
    else:
        return "Label not found."


def scrap_person_data():
    try:
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

        # --- Generate Name Variations ---
        potential_manipulated_names = []
        if full_name:
            parts = full_name.split()
            first_name = parts[0] if parts else ""
            last_name = parts[-1] if len(parts) > 1 else ""

            if full_name.strip():
                potential_manipulated_names.append(full_name.strip())
                potential_manipulated_names.append(randomize_first_letter_case(full_name.strip()))
            if first_name.strip():
                potential_manipulated_names.append(first_name.strip())
                if last_name.strip():
                    potential_manipulated_names.append(f"{first_name.strip()} {last_name.strip()}")
                    potential_manipulated_names.append(f"{first_name.strip()} {last_name.strip()[0]}.")

        if not potential_manipulated_names:
            potential_manipulated_names.append(full_name.strip() if full_name else "") # Fallback

        manipulated_name = random.choice(potential_manipulated_names)

        username = username.strip() if username else ""
        print("Username: ", username)

        name_options = [name for name in [manipulated_name, username] if name]
        if not name_options:
            name_options = ["DefaultName"]

        pin_img = pinterest()
        image_url = random.choice([avatar_url, pin_img])
        imgur_url = imgur_uploader(scraper, image_url)
        return name_options, gender, selected_bio, job_title_input, city, imgur_url

    except Exception as e:
        print("Error:", e)
        return ["DefaultName"], "", "", "", "", ""
        # restart_warp()


def get_mail(x=None):
    global wait, driver, circle, mail, tabs
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


def activate_user(email, pw):
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
    headers = {'Authorization': 'Token ceLDhha7NKK6QMY2LU79B6EPc7LuUfrz'}
    response = requests.request("POST", url, headers=headers, data=payload)
    print(response.json())
    return


create_db()
while True:
    name_list, gender, bio, headline, city, avatar = scrap_person_data()
    fullname = random.choice(name_list)
    print("Fullname: ", fullname)
    mailstring = get_mail(x="mail")
    pw = generate_password()
    create_person()
    activate_user(email=mailstring, pw=pw)
    insert_users(fullname, mailstring, pw, bio, headline, avatar)
