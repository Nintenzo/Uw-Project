import requests
import re
import time
import random
import csv
import os
import string
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


def randomize_first_letter_case(text):
    if not text:
        return ""
    result = random.choices([text, text.lower(), text.upper()], [0.475, 0.475, 0.05])[0]
    return result

def manipulate_username(username):
    if not username:
        return ""

    original_username = username
    n_changes = random.randint(1, 2)
    possible_ops = []
    current_username_list = list(username)

    for i in range(n_changes):
        possible_ops = []
        if len(current_username_list) > 0:
            possible_ops.append('add')
        if len(current_username_list) > 1:
            possible_ops.append('delete')
            possible_ops.append('swap')

        if not possible_ops:
            break

        op = random.choice(possible_ops)

        try:
            if op == 'delete':
                del_index = random.randrange(len(current_username_list))
                del current_username_list[del_index]
            elif op == 'add':
                add_char = random.choice(string.ascii_lowercase)
                add_index = random.randrange(len(current_username_list) + 1)
                current_username_list.insert(add_index, add_char)
            elif op == 'swap':
                swap_index = random.randrange(len(current_username_list) - 1)
                current_username_list[swap_index], current_username_list[swap_index + 1] = current_username_list[swap_index + 1], current_username_list[swap_index]
        except IndexError:
             print(f"Warning: IndexError during username manipulation ('{op}' on '{''.join(current_username_list)}'). Skipping change.")
             continue
    modified_username = "".join(current_username_list)
    if modified_username == original_username:
        modified_username += str(random.randint(0, 9))
        if modified_username == original_username:
             return original_username + "_mod"

    return modified_username


def get_username(scraped_username, csv_filepath='users.csv'):
	scraped_username = scraped_username.strip()
	selected_final_value = None
	third_column_value = None
	rows = []
	pin = True
	try:
		if os.path.exists(csv_filepath):
			with open(csv_filepath, 'r', newline='', encoding='utf-8') as f:
				reader = csv.reader(f)
				rows = [row for row in reader if len(row) >= 2 and row[0].strip() and row[1].strip()]

			if rows:
				chosen_row_index = random.randint(0, len(rows) - 1)
				username = rows[chosen_row_index][0].strip()
				name = rows[chosen_row_index][1].strip()

				# Get third column value if it exists
				if len(rows[chosen_row_index]) >= 3:
					third_column_value = rows[chosen_row_index][2].strip()

				if random.choice([True, False]):
					selected_final_value = manipulate_username(username)
					pin = False
					print(f"Using manipulated username: {selected_final_value}")
				else:
					selected_final_value = name
					print(f"Using full name: {selected_final_value}")

				# Remove used row
				del rows[chosen_row_index]

				# Save remaining rows back to CSV
				with open(csv_filepath, 'w', newline='', encoding='utf-8') as f:
					writer = csv.writer(f)
					writer.writerows(rows)
			else:
				print(f"Warning: No valid rows in {csv_filepath}.")
		else:
			print(f"Warning: {csv_filepath} not found.")
	except Exception as e:
		print(f"Error processing {csv_filepath}: {e}")

	# Fallback if no valid value was chosen
	if not selected_final_value:
		if scraped_username:
			selected_final_value = scraped_username
			print(f"Fallback to scraped username: {selected_final_value}")
		else:
			selected_final_value = "DefaultUsername"
			print("Warning: No valid data. Using default username.")

	return [selected_final_value, third_column_value, pin]


scraper = cloudscraper.create_scraper()
url = "https://app.circle.so/api/v1/community_members"

def create_driver():
    global driver
    driver = Driver(uc=True, incognito=True, headless=True)
    return driver

def pinterest(name,gender,add):
    try:
        pinterest_keywords = [f"{cat} {mod}" for cat in categories for mod in modifiers]
        driver = create_driver()
        WebDriverWait(driver, 60)
        key = random.choices([random.choice(pinterest_keywords), name], [0.6, 0.4])[0]
        
        if add:
            search = f"{key} {gender}"
            print(f"Searching Pinterest for: {search}")
            url = f"https://www.pinterest.com/search/pins/?q={search}"
            driver.get(url)
        else:
            print(f"Searching Pinterest for: {key}")
            url = f"https://www.pinterest.com/search/pins/?q={key}"
            driver.get(url)
        print(url)
        for _ in range(1):
            time.sleep(1.5)
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)
        image_urls = []
        for _ in range(10):
            try:
                images_containers = driver.find_elements(By.CSS_SELECTOR, ".Yl-.MIw.Hb7")
                numbers = [x for x in range(0, len(images_containers))]
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
    except Exception as e:
        driver.quit()
        print(f"Error: {e}")
        time.sleep(1)
        pinterest(name,gender,add)


def get_next_sibling_text(label_text, soup):
    label = soup.find(string=label_text)
    if label:
        return label.find_next().get_text(strip=True)
    else:
        return "Label not found."

def get_job(scraper):
    while True:
        url = "https://writingexercises.co.uk/php_WE/job.php?_=1745167420134"
        job = scraper.get(url)
        if job.text == "Fisherman/woman":
            continue
        return randomize_first_letter_case(job.text)

def scrap_person_data():
    try:
        url = "https://www.fakepersongenerator.com/Index/generate"
        response = scraper.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        image_srcs = [tag['src'] for tag in soup.find_all(src=lambda s: s and s.startswith('/Face'))]
        avatar_url = f"https://www.fakepersongenerator.com{image_srcs[0]}" if image_srcs else None
        headline = get_job(scraper)
        bio_labels = ["Online Status", "Online Signature", "Online Biography"]
        bios = [get_next_sibling_text(label, soup) for label in bio_labels if get_next_sibling_text(label, soup)]
        bios.append("")
        selected_bio = random.choice(bios) if bios else ""
        gender = city = ""
        details_div = soup.find("div", class_="col-md-8 col-sm-6 col-xs-12")
        if details_div:
            text = details_div.get_text(separator=" ", strip=True)
            if "Gender:" in text:
                gender = text.split("Gender:")[1].split()[0].strip()
            if "City, State, Zip:" in text:
                city = text.split("City, State, Zip:")[1].split(",")[0].strip()
        raw_username = get_next_sibling_text("Username", soup)
        job_title_input = ["",headline]
        job_title_input = random.choice(job_title_input)
        final_username = get_username(raw_username)
        print(final_username[0])
        print(final_username[1])
        print(final_username[2])
        pin_img = pinterest(final_username[0],final_username[1],final_username[2])
        image_url = random.choice([avatar_url, pin_img])
        imgur_url = imgur_uploader(scraper, image_url)
        image = random.choices([imgur_url, " "], [0.9, 0.1])[0]
        return final_username[0], gender, selected_bio, job_title_input, city, image
    except Exception as e:
        print("Error:", e)
        restart_warp()


def get_mail(x=None):
    global wait, driver, circle, mail, tabs
    if x == "mail":
        driver = create_driver()
        wait = WebDriverWait(driver, 601)
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
    while True:
        try:
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
        except Exception as e:
            print(e)
            continue

create_db()
count = 0
while True:
    try:
        count +=1
        name_list, gender, bio, headline, city, avatar = scrap_person_data()
        fullname = name_list
        print("Fullname: ", fullname)
        mailstring = get_mail(x="mail")
        pw = generate_password()
        create_person()
        activate_user(email=mailstring, pw=pw)
        insert_users(fullname, mailstring, pw, bio, headline, avatar)
        print(count)
        if count == 50:
            break
    except Exception as e:
        print(e)