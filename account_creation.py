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
from identity_data import LGBT_IDENTITIES, get_pronouns


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


def format_bio_with_pronouns(bio, pronouns):
    """Generates a bio string including pronouns in a variety of more human formats."""
    bio = bio.strip() if bio else ""
    pronouns = pronouns.strip() if pronouns else None

    if not pronouns:
        return bio

    emoji_list = ["✨", "😊", "🌱", "🏳️‍🌈", "🏳️‍⚧️", "💖", "✌️", "👋"]
    add_emoji = random.random() < 0.3

    # Expanded list of pronoun introducers
    pronoun_keywords = [
        "Pronouns:", "pronouns:", "p:", "My pronouns:", "Pronouns",
        "pronouns",
        "Uses",
        "Prefers"
    ]
    chosen_keyword = random.choice(pronoun_keywords)
    # Occasionally remove colon if present
    if random.random() < 0.2 and chosen_keyword.endswith(":"):
        chosen_keyword = chosen_keyword[:-1]

    # Formats when the original bio is empty
    pronoun_only_formats = [
        f"{pronouns}",
        f"{chosen_keyword} {pronouns}",
        f"({pronouns})",
        f"[{pronouns}]",
        f"Just {pronouns}",
        f"Call me {pronouns}!",
        f"Respect the {pronouns}",
        f"{pronouns.capitalize()}"
    ]

    # Split combined formats for balanced selection
    formats_pronouns_first = [
        f"{chosen_keyword} {pronouns}. {bio}",
        f"[{pronouns}] {bio}",
        f"({pronouns}) {bio}",
        f"{pronouns} || {bio}",
        f"{pronouns} ~ {bio}",
        f"{pronouns.capitalize()} | {bio}"
    ]
    formats_bio_first = [
        f"{bio} ({pronouns})",
        f"{bio} [{pronouns}]",
        f"{bio} | {pronouns}",
        f"{bio} - {pronouns}",
        f"{bio} ({chosen_keyword} {pronouns})",
        f"{bio} (my pronouns are {pronouns})",
        f"{bio}. {chosen_keyword} {pronouns}.",
        f"{bio} // {pronouns}",
        f"{bio}. ({pronouns})"
    ]

    if not bio:
        formatted_bio = random.choice(pronoun_only_formats)
    else:
        if random.choice([True, False]):
            formatted_bio = random.choice(formats_pronouns_first)
        else:
            formatted_bio = random.choice(formats_bio_first)

    if add_emoji:
        formatted_bio += f" {random.choice(emoji_list)}"

    return formatted_bio.strip()


def get_username(target_identity, original_gender, scraped_username, csv_filepath='users.csv'):
    """Gets a name/username, filtering CSV based on target identity.

    Args:
        target_identity (str): The desired identity (Male, Female, Lesbian, Gay, etc.).
        original_gender (str): The originally scraped gender (for Trans cases).
        scraped_username (str): The username scraped from the website (fallback).
        csv_filepath (str): The path to the CSV file (username, name, gender).

    Returns:
        list: [chosen_value, csv_gender, use_name_from_csv_bool]
              Returns [scraped_username, None, False] on failure or no match.
    """
    scraped_username = scraped_username.strip()
    selected_final_value = None
    chosen_csv_gender = None
    pin = False
    rows = []
    all_rows_read = []

    try:
        if os.path.exists(csv_filepath):
            with open(csv_filepath, 'r', newline='', encoding='utf-8') as f:
                reader = csv.reader(f)
                # Read all rows with at least 3 columns
                all_rows_read = [row for row in reader if len(row) >= 3 and all(c.strip() for c in row[:3])]

            # --- Filter rows based on target_identity ---
            filtered_rows = []
            target_identity_cap = target_identity.capitalize()
            original_gender_cap = original_gender.capitalize() if original_gender else None

            for row in all_rows_read:
                csv_gender = row[2].strip().capitalize()
                match = False
                if target_identity_cap in ["Male", "Gay"] and csv_gender == "Male":
                    match = True
                elif target_identity_cap in ["Female", "Lesbian"] and csv_gender == "Female":
                    match = True
                elif target_identity_cap == "Bisexual" and csv_gender in ["Male", "Female"]:
                     match = True
                elif target_identity_cap == "Transgender":
                    # Match Male names if original gender was Female (Trans Man)
                    if original_gender_cap == "Female" and csv_gender == "Male":
                        match = True
                    # Match Female names if original gender was Male (Trans Woman)
                    elif original_gender_cap == "Male" and csv_gender == "Female":
                        match = True
                
                if match:
                    filtered_rows.append(row)

            print(f"Target: {target_identity_cap}, Orig G: {original_gender_cap}. Found {len(filtered_rows)} matching CSV rows.")

            if filtered_rows:
                # --- Choose from filtered rows ---
                chosen_row = random.choice(filtered_rows)
                chosen_row_index_in_original = all_rows_read.index(chosen_row) # Find index in original list
                
                username = chosen_row[0].strip()
                name = chosen_row[1].strip()
                chosen_csv_gender = chosen_row[2].strip()

                # 50/50 choice: use name or manipulated username
                if random.choice([True, False]): # True = Use Manipulated Username
                    selected_final_value = manipulate_username(username)
                    pin = False # Indicates manipulated username chosen
                    print(f"Using manipulated username from CSV: {selected_final_value}")
                else: # False = Use Name
                    selected_final_value = name
                    pin = True # Indicates name chosen
                    print(f"Using full name from CSV: {selected_final_value}")

                # Remove the *chosen* row from the *original* list
                del all_rows_read[chosen_row_index_in_original]

                # Save remaining rows back to CSV
                with open(csv_filepath, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerows(all_rows_read)
            else:
                print(f"Warning: No CSV rows match target identity '{target_identity}'.")
        else:
            print(f"Warning: {csv_filepath} not found.")
    except Exception as e:
        print(f"Error processing {csv_filepath}: {e}")

    # Fallback if no value selected from CSV
    if selected_final_value is None:
        if scraped_username:
            selected_final_value = scraped_username
            chosen_csv_gender = None # No gender info from fallback
            pin = False # Indicates fallback/scraped username
            print(f"Fallback to scraped username: {selected_final_value}")
        else:
            selected_final_value = "DefaultUsername"
            chosen_csv_gender = None
            pin = False
            print("Warning: No valid data. Using default username.")

    # Return chosen name/username, the gender from the chosen CSV row (or None), and the boolean
    return [selected_final_value, chosen_csv_gender, pin]


scraper = cloudscraper.create_scraper()
url = "https://app.circle.so/api/v1/community_members"

def create_driver():
    global driver
    driver = Driver(uc=True, incognito=True, headless=False)
    return driver

def pinterest(name, gender, add):
    try:
        print("add: ", add)
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

        # --- Get Original Gender and Determine Final Identity/Pronouns ---
        original_gender = ""
        details_div = soup.find("div", class_="col-md-8 col-sm-6 col-xs-12")
        if details_div:
            text = details_div.get_text(separator=" ", strip=True)
            if "Gender:" in text:
                original_gender = text.split("Gender:")[1].split()[0].strip()
            if "City, State, Zip:" in text:
                 city = text.split("City, State, Zip:")[1].split(",")[0].strip()
        else:
            city = ""

        final_identity = original_gender
        pronouns = None
        if random.randint(1, 100) <= 9:
            final_identity = random.choice(LGBT_IDENTITIES)
            pronouns = get_pronouns(final_identity, original_gender)
            print(f"Selected LGBT Identity: {final_identity}, Pronouns: {pronouns}")
            selected_bio = format_bio_with_pronouns(selected_bio, pronouns)
        else:
            final_identity = original_gender
            print(f"Selected Identity: {final_identity}")

        # --- Username and Name Selection (using get_username) ---
        raw_username = get_next_sibling_text("Username", soup)
        username_data = get_username(final_identity, original_gender, raw_username)
        final_name_or_username = username_data[0]
        use_pin_search_modifier_from_csv = username_data[2]

        job_title_input = ["", headline]
        job_title_input = random.choice(job_title_input)

        # --- Determine final Pinterest search modifier ---
        if final_identity in LGBT_IDENTITIES:
            add_term_to_pinterest_search = True # Force add for LGBT
            print("Forcing Pinterest identity search for LGBT identity.")
        else:
            # For Male/Female, respect the boolean from get_username
            add_term_to_pinterest_search = use_pin_search_modifier_from_csv
            print(f"Pinterest identity search for Male/Female determined by CSV logic: {add_term_to_pinterest_search}")

        # --- Image Selection ---
        pin_img = pinterest(final_name_or_username, final_identity, add_term_to_pinterest_search)
        image_url = random.choice([avatar_url, pin_img])
        imgur_url = imgur_uploader(scraper, image_url)
        final_image = random.choices([imgur_url, " "], [0.9, 0.1])[0]

        return final_name_or_username, original_gender, final_identity, selected_bio, job_title_input, city, final_image

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
        count += 1
        # Unpack the new return values from scrap_person_data
        final_name, scraped_gender, identity, bio, headline, city, avatar = scrap_person_data()
        # Assign to fullname for use in create_person/insert_users
        fullname = final_name

        print(f"Chosen Name: {fullname}, Scraped Gender: {scraped_gender}, Final Identity: {identity}")
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