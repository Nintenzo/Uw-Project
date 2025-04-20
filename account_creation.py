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
    first_char = random.choice([text[0].upper(), text[0].lower()])
    return first_char + text[1:]


def manipulate_username(username):
    if not username:
        return ""

    original_username = username
    n_changes = random.randint(1, 2)
    possible_ops = []
    current_username_list = list(username)

    for i in range(n_changes):
        # Refresh possible operations based on current state
        possible_ops = []
        if len(current_username_list) > 0:
            possible_ops.append('add')
        if len(current_username_list) > 1:
            possible_ops.append('delete')
            possible_ops.append('swap') # Swap adjacent

        if not possible_ops:
            break # Cannot perform any more operations

        op = random.choice(possible_ops)

        try:
            if op == 'delete':
                del_index = random.randrange(len(current_username_list))
                del current_username_list[del_index]
            elif op == 'add':
                add_char = random.choice(string.ascii_lowercase) # Add lowercase letter
                add_index = random.randrange(len(current_username_list) + 1)
                current_username_list.insert(add_index, add_char)
            elif op == 'swap':
                swap_index = random.randrange(len(current_username_list) - 1)
                current_username_list[swap_index], current_username_list[swap_index + 1] = current_username_list[swap_index + 1], current_username_list[swap_index]
        except IndexError:
             print(f"Warning: IndexError during username manipulation ('{op}' on '{''.join(current_username_list)}'). Skipping change.")
             continue # Skip this change if index was bad


    modified_username = "".join(current_username_list)

    # Ensure it's different from original, force if needed
    if modified_username == original_username:
        modified_username += str(random.randint(0, 9))
        # If still same (e.g., empty string?), return original or a default
        if modified_username == original_username:
             return original_username + "_mod" # Very unlikely fallback

    return modified_username


def get_username(scraped_username, csv_filepath='users.csv'):
    """Gets a username, choosing between scraped and one from a CSV file.

    Args:
        scraped_username (str): The username scraped from the website.
        csv_filepath (str): The path to the CSV file containing usernames.

    Returns:
        str: The chosen username.
    """
    scraped_username = scraped_username.strip()
    chosen_original_csv_username = None # Track the originally chosen CSV username
    manipulated_csv_username = None   # Track the modified version
    read_usernames = []

    try:
        if os.path.exists(csv_filepath):
            with open(csv_filepath, 'r', newline='', encoding='utf-8') as f:
                reader = csv.reader(f)
                read_usernames = [row[0].strip() for row in reader if row and row[0].strip()]

            if read_usernames:
                chosen_original_csv_username = random.choice(read_usernames)
                # Manipulate the chosen CSV username
                manipulated_csv_username = manipulate_username(chosen_original_csv_username)
                print(f"CSV User: Original='{chosen_original_csv_username}', Manipulated='{manipulated_csv_username}'") # Debug info
        else:
            print(f"Warning: {csv_filepath} not found.")

    except Exception as e:
        print(f"Error reading/processing {csv_filepath}: {e}")

    # --- Decide final username ---
    options = []
    if scraped_username:
        options.append(scraped_username)
    if manipulated_csv_username: # Use the manipulated username as an option
        options.append(manipulated_csv_username)

    if not options:
        print("Warning: No valid usernames available. Using default.")
        return "DefaultUsername"

    final_username = random.choice(options)
    print(f"Final Username Chosen: '{final_username}'")

    # --- Remove ORIGINAL from CSV if MANIPULATED CSV username was selected ---
    if final_username == manipulated_csv_username and chosen_original_csv_username is not None:
        print(f"Manipulated username '{final_username}' (from '{chosen_original_csv_username}') selected. Removing original from CSV...")
        # Use the originally read list to filter from
        remaining_usernames = [u for u in read_usernames if u != chosen_original_csv_username]
        try:
            with open(csv_filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                for username in remaining_usernames:
                    writer.writerow([username])
            print(f"Original '{chosen_original_csv_username}' removed from {csv_filepath}.")
        except Exception as e:
            print(f"Error writing back to {csv_filepath}: {e}")
            # Consider how to handle this: the username was used but not removed.

    return final_username


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

        # --- Process Username ---
        # Get raw username from scraping
        raw_username = get_next_sibling_text("Username", soup)
        # Get the final username (potentially from CSV, with removal logic)
        final_username = get_username(raw_username) # Calls the new function

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
            potential_manipulated_names.append(full_name.strip() if full_name else "")

        # --- Choose one manipulated name (with weighting) ---
        if len(potential_manipulated_names) > 1:
            weights = []
            original_weight = 1
            other_weight = 5
            original_full_name_str = full_name.strip() if full_name else ""

            for name_option in potential_manipulated_names:
                if name_option == original_full_name_str:
                    weights.append(original_weight)
                else:
                    weights.append(other_weight)

            if len(weights) == len(potential_manipulated_names):
                manipulated_name = random.choices(potential_manipulated_names, weights=weights, k=1)[0]
            else:
                print("Warning: Weight/Name list mismatch. Falling back to equal choice.")
                manipulated_name = random.choice(potential_manipulated_names)
        elif potential_manipulated_names:
            manipulated_name = potential_manipulated_names[0]
        else:
            manipulated_name = "DefaultManipulatedName"

        # --- Final list for selection (Manipulated Name OR Final Username) ---
        name_options = [name for name in [manipulated_name, final_username] if name]
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
