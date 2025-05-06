import requests
import re
import time
import random
import csv
import os
import string
import cloudscraper
import threading
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from services.db_service import create_db_users, insert_users, fetch_spaces_id
from services.password_service import generate_password
from services.warp_service import restart_warp
from settings.cities import uscities
from services.driver_services import create_driver
from settings.bio_keywords import bio_words
from settings.headlines_keywords import common_jobs
import subprocess
from services.pinterest_api import get_img
from identity_data import LGBT_IDENTITIES, get_pronouns
from services.cookies_service import get_cookies
from dotenv import load_dotenv

load_dotenv()
try:
    csv.field_size_limit(min(2**30, csv.field_size_limit() * 10))
except OverflowError:
    print("Warning: Could not significantly increase CSV field size limit.")
    csv.field_size_limit(131072 * 2)

scraper = cloudscraper.create_scraper()

CIRCLE_API_URL = "https://app.circle.so/api/v1/community_members"
COMMUNITY_ID = os.getenv("COMMUNITY_ID")
CSV_FILEPATH = 'users.csv'
CIRCLE_AUTH_TOKEN = f'Token {os.getenv("CIRCLE_API")}'

csv_lock = threading.Lock()
counter_lock = threading.Lock()
db_lock = threading.Lock()

accounts_created_count = 0

db_conn, db_cursor = create_db_users()

def kill_chrome_and_driver():
	processes = [("chrome.exe", "Chrome"), ("chromedriver.exe", "ChromeDriver")]
	for proc_name, label in processes:
		try:
			result = subprocess.run(
				["taskkill", "/F", "/IM", proc_name, "/T"],
				capture_output=True,
				text=True
			)
		except subprocess.CalledProcessError as e:
			pass


def get_space_ids():
    """Fetches space IDs from the database."""
    try:
        spaces_data = fetch_spaces_id("space_id").fetchall()
        return [x[0] for x in spaces_data]
    except Exception as e:
        print(f"Error fetching space IDs: {e}")
        return []

SPACE_IDS = get_space_ids()

def randomize_first_letter_case(text):
    if not text:
        return ""
    return random.choice([text, text.lower(), text.upper()])

def manipulate_username(username):
    if not username:
        return ""

    original_username = username
    current_username_list = list(username)
    n_changes = random.randint(1, 2)

    for _ in range(n_changes):
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
            if op == 'delete' and len(current_username_list) > 0:
                del_index = random.randrange(len(current_username_list))
                del current_username_list[del_index]
            elif op == 'add':
                add_char = random.choice(string.ascii_lowercase)
                add_index = random.randrange(len(current_username_list) + 1)
                current_username_list.insert(add_index, add_char)
            elif op == 'swap' and len(current_username_list) > 1:
                swap_index = random.randrange(len(current_username_list) - 1)
                (current_username_list[swap_index],
                 current_username_list[swap_index + 1]) = (
                    current_username_list[swap_index + 1],
                    current_username_list[swap_index]
                )
        except (IndexError, ValueError) as e:
            print(f"Warning: Handled error during username manipulation "
                  f"('{op}' on '{''.join(current_username_list)}'): {e}. Skipping change.")
            continue

    modified_username = "".join(current_username_list)

    if modified_username == original_username:
        modified_username += str(random.randint(0, 9))
        if modified_username == original_username:
             return original_username + "_mod"

    return modified_username

def get_bio(input1):
    try:
        words_list = random.choices(bio_words,k=random.randint(1,4))
        for x in words_list:
            input1 += f" {x}" 
        
        url = "https://www.hootsuite.com/api/contentGenerator"
        payload = {"dropdown1": "Instagram",
                "dropdown2": "Personal",
                "dropdown3": random.choice(["None","Just for fun"]),
                "id": "rUQh7Ij1GC8Nxprlng4JY",
                "input1": f"{input1} (do not make this bio instagram by adding words such as follow, connect, join etc related make it general and usable everywhere)",
                "input2": "",
                "locale": "en-US"}
        request = requests.get(url, data=payload, timeout=10)
        request = request.json()
        return request.get('results')[random.randint(1,2)][3:]
    except IndexError:
        print(f"Error generating bio: {e} Returning empty bio")
        print(input1)
        return ""
    except Exception as e:
        print(f"Error generating bio: {e}")
        print(input1)
        if WARP:
            restart_warp()
        return ""

def read_all_users_from_csv():
    """Reads all valid user rows from the CSV."""
    all_rows = []
    if not os.path.exists(CSV_FILEPATH):
        print(f"Error: {CSV_FILEPATH} not found.")
        return None

    try:
        with open(CSV_FILEPATH, 'r', newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            all_rows = [
                row for row in reader
                if len(row) >= 3 and all(c.strip() for c in row[:3])
            ]
        print(f"Read {len(all_rows)} valid user rows from {CSV_FILEPATH}.")
        return all_rows
    except Exception as e:
        print(f"Error reading {CSV_FILEPATH}: {e}")
        return None

def get_and_remove_user_from_list(user_list, target_identity, original_gender):
    if user_list is None:
        return None, None, False, None

    target_identity_cap = target_identity.capitalize()
    original_gender_cap = original_gender.capitalize() if original_gender else None

    def filter_rows(rows, identity_cap, gender_cap):
        filtered_indices = []
        for i, row in enumerate(rows):
            if len(row) < 3: continue
            csv_gender = row[2].strip().capitalize()
            match = False
            if identity_cap in ("Male", "Gay") and csv_gender == "Male":
                match = True
            elif identity_cap in ("Female", "Lesbian") and csv_gender == "Female":
                match = True
            elif identity_cap == "Bisexual" and csv_gender in ("Male", "Female"):
                match = True
            elif identity_cap == "Transgender":
                if gender_cap == "Female" and csv_gender == "Male":
                    match = True
                elif gender_cap == "Male" and csv_gender == "Female":
                    match = True
            if match:
                filtered_indices.append(i)
        return filtered_indices

    with csv_lock:
        if not user_list:
             print(f"Warning: User list is empty. Cannot select user for {target_identity}.")
             return None, None, False, None

        filtered_indices = filter_rows(user_list, target_identity_cap, original_gender_cap)

        if not filtered_indices and target_identity_cap in ("Male", "Gay", "Female", "Lesbian"):
            alt_identity = "Female" if target_identity_cap in ("Male", "Gay") else "Male"
            print(f"No users for {target_identity_cap}, trying fallback {alt_identity}...")
            filtered_indices = filter_rows(user_list, alt_identity, original_gender_cap)
            if filtered_indices:
                print(f"Found users for fallback identity {alt_identity}.")
            else:
                print(f"No users found for fallback identity {alt_identity} either.")

        if filtered_indices:
            chosen_relative_index = random.choice(filtered_indices)
            chosen_row = user_list.pop(chosen_relative_index)

            username = chosen_row[0].strip()
            name = chosen_row[1].strip()
            chosen_csv_gender = chosen_row[2].strip()

            use_full_name = random.choice([True, False])
            if use_full_name:
                selected_final_value = name
                pin_search_modifier = True
            else:
                selected_final_value = manipulate_username(username)
                pin_search_modifier = False

            # print(f"Successfully selected and removed user for {target_identity}. Remaining users: {len(user_list)}")
            return selected_final_value, chosen_csv_gender, pin_search_modifier, chosen_row

        else:
            print(f"Warning: No CSV rows match target identity '{target_identity}' "
                  f"(Gender: {original_gender_cap}) or fallbacks.")
            return None, None, False, None

def rewrite_csv(remaining_rows):
    with csv_lock:
        try:
            with open(CSV_FILEPATH, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerows(remaining_rows)
            print(f"Successfully rewrote {CSV_FILEPATH} with {len(remaining_rows)} remaining users.")
            return True
        except Exception as e:
            print(f"Error rewriting {CSV_FILEPATH}: {e}")
            return False

def pinterest_scrape(driver, name_or_username, search_identity, use_identity_in_search, original_gender):
    MAX_RETRIES = 2
    for attempt in range(MAX_RETRIES):
        try:
            base_key = name_or_username
            if use_identity_in_search:
                search_term = f"{base_key} {search_identity}"
            else:
                search_term = f"{base_key} {original_gender}"

            search_term += random.choice(["", " pfp", " aesthetic", " portrait"])
            search_term = search_term.replace("  ", " ").strip()

            search_query = requests.utils.quote(search_term)
            url = f"https://www.pinterest.com/search/pins/?q={search_query}"
            driver.get(url)

            image_urls = set()
            image_containers = driver.find_elements(By.CSS_SELECTOR, "div[data-test-id='pin'] img")

            if not image_containers:
                 image_containers = driver.find_elements(By.TAG_NAME, "img")


            for img in image_containers:
                try:
                    src = img.get_attribute("src")
                    if src and src.startswith('https://i.pinimg.com'):
                        image_urls.add(src)
                except Exception:
                    pass

            if not image_urls:
                print(f"Thread {threading.get_ident()}: Warning - No suitable image URLs found on Pinterest for '{search_term}'. Retrying...")
                return None

            chosen_img_url = random.choice(list(image_urls))

            return chosen_img_url

        except Exception as e:
            print(f"Thread {threading.get_ident()}: Error during Pinterest scrape (Attempt {attempt + 1}/{MAX_RETRIES}): {e}")
            if attempt < MAX_RETRIES - 1:
                return None

    return None

def scrap_person_data(user_list):
    try:
        headline = randomize_first_letter_case(random.choice(common_jobs))
        original_gender = random.choice(["male", "female"])
        final_identity = original_gender
        pronouns = None

        if random.randint(1, 100) <= 10:
            potential_identities = [i for i in LGBT_IDENTITIES if i != "Unknown"]
            if potential_identities:
                final_identity = random.choice(potential_identities)
                pronouns = get_pronouns(final_identity, original_gender)
            else:
                 final_identity = original_gender


        name_or_username, csv_gender, use_pin_search_modifier, chosen_csv_row = \
            get_and_remove_user_from_list(user_list, final_identity, original_gender)

        if name_or_username is None:
            print(f"Thread {threading.get_ident()}: Failed to get user from CSV list for {final_identity}. Skipping account creation.")
            return None

        search_pinterest_with_identity = (final_identity in LGBT_IDENTITIES) or use_pin_search_modifier
        city = random.choice(uscities + [""])
        return {
            "name": name_or_username,
            "original_gender": original_gender,
            "identity": final_identity,
            "pronouns": pronouns,
            "headline": random.choice(["", headline]),
            "city": city,
            "csv_gender": csv_gender,
            "use_pinterest_identity_search": search_pinterest_with_identity,
            "chosen_csv_row": chosen_csv_row
        }

    except Exception as e:
        print(f"Thread {threading.get_ident()}: Error in scrap_person_data: {e}")
        return None

def get_mail_and_code(driver, wait, get_code=False):
    EMAIL_XPATH = "//div[contains(@class, 'text-foreground')]"
    CODE_CSS_SELECTOR = '.flex.lg\\:justify-start.text-sm.font-medium.truncate.text-gray-900'

    try:
        if not get_code:
            driver.get('https://minmail.app/10-minute-mail')
            mail_window = driver.current_window_handle
            driver.execute_script("window.open('https://login.circle.so/sign_in?request_host=app.circle.so#email', '_blank');")

            all_handles = driver.window_handles
            circle_window = [h for h in all_handles if h != mail_window][0]

            driver.switch_to.window(mail_window)
            email_div = wait.until(EC.visibility_of_element_located((By.XPATH, EMAIL_XPATH)))
            email = email_div.text.strip()
            return email, mail_window, circle_window
        else:
            wait = WebDriverWait(driver, 15)
            code_element = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, CODE_CSS_SELECTOR)))
            code_text = code_element.text
            match = re.search(r'\b(\d{6})\b', code_text)
            if match:
                code = match.group(1)
                return code
            else:
                 digits = re.findall(r'\d+', code_text)
                 if digits:
                     code = ''.join(digits)
                     print(f"Thread {threading.get_ident()}: Extracted code (fallback): {code}")
                     return code
                 else:
                    print(f"Thread {threading.get_ident()}: Error - Could not extract digits from code text: {code_text}")
                    return None

    except Exception as e:
        print(f"Thread {threading.get_ident()}: Error in get_mail_and_code (get_code={get_code}): {e}")
        return None

def activate_user_selenium(driver, wait, email, password, mail_window, circle_window):
    global accounts_created_count, count

    try:
        print(f"Thread {threading.get_ident()}: Activating account for {email}...")
        driver.switch_to.window(circle_window)

        email_form = wait.until(EC.visibility_of_element_located((By.NAME, "user[email]")))
        email_form.send_keys(email)
        pw_form = wait.until(EC.visibility_of_element_located((By.NAME, "user[password]")))
        pw_form.send_keys(password)
        pw_form.send_keys(Keys.ENTER)

        driver.switch_to.window(mail_window)
        code = get_mail_and_code(driver, wait, get_code=True)
        if not code:
            print(f"Thread {threading.get_ident()}: Failed to get activation code for {email}.")
            return None

        driver.switch_to.window(circle_window)
        otp_element = wait.until(EC.visibility_of_element_located((By.NAME, "otp")))
        otp_element.send_keys(code)

        continue_button = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//button[@type='submit' and (contains(text(),'Continue') or contains(text(),'Verify'))]")
        ))
        continue_button.click()

        target_url = "https://tubiit.circle.so/feed"
        try:
            WebDriverWait(driver, 45).until(EC.url_to_be(target_url))

            cookie_values = get_cookies(driver, ["remember_user_token", "user_session_identifier"])
            if cookie_values:
                remember_token, session_id = cookie_values[0], cookie_values[1]
                print(f"Thread {threading.get_ident()}: Account activated successfully for {email}.")
                with counter_lock:
                    accounts_created_count += 1
                    print(f"--- Accounts created so far: {accounts_created_count} ---")
                return remember_token, session_id
            else:
                print(f"Thread {threading.get_ident()}: Failed to get required cookies after activation for {email}. Expected tuple of 2 values, got: {cookie_values}")
                return None

        except Exception as e:
             print(f"Thread {threading.get_ident()}: Error waiting for redirect or getting cookies for {email}: {e}")
             return None

    except Exception as e:
        print(f"Thread {threading.get_ident()}: Unexpected error during Selenium activation for {email}: {e}")
        return None

def create_person_api(email, password, profile_data):
    payload = {
        "email": email,
        "password": password,
        "name": profile_data['name'],
        "bio": profile_data.get('bio', ''),
        "headline": profile_data.get('headline', ''),
        "avatar": profile_data.get('avatar_url', ''),
        "community_id": COMMUNITY_ID,
        "space_ids": SPACE_IDS,
        "skip_invitation": False,
        "location": profile_data.get('city', '')
    }
    headers = {'Authorization': CIRCLE_AUTH_TOKEN}
    try:
        response = requests.post(CIRCLE_API_URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()
        user_data = data.get('user')
        if user_data and user_data.get('id') and user_data.get('public_uid') and user_data.get('community_member_id'):
            return (
                user_data['id'],
                user_data['public_uid'],
                user_data['community_member_id']
            )
        else:
            print(f"Thread {threading.get_ident()}: API response missing user details for {email}. Response: {data}")
            return None
    except Exception as e:
            print(f"Thread {threading.get_ident()}: Unexpected error during API creation for {email}: {e}")
            return None

def insert_user_db(profile_data, email, password, api_ids, cookies):
    member_id, public_uid, community_member_id = api_ids
    remember_token, session_id = cookies

    with db_lock:
        try:
             if not db_conn or not db_cursor:
                  print("Error: Database connection/cursor not available.")
                  return False

             insert_users(
                 profile_data['name'], email, password,
                 profile_data['identity'], profile_data['original_gender'],
                 profile_data.get('pronouns'),
                 profile_data.get('bio', ''),
                 profile_data.get('headline', ''),
                 profile_data.get('city', ''),
                 profile_data.get('avatar_url', ''),
                 remember_token, session_id,
                 member_id, public_uid, community_member_id
             )
             print(f"Thread {threading.get_ident()}: Database insertion successful for {email}.")
             return True
        except Exception as e:
             print(f"Thread {threading.get_ident()}: Error inserting user {email} into database: {e}")
             return False

def account_creation_worker(worker_id, user_list):
    global accounts_created_count

    print(f"Worker {worker_id}: Starting...")
    driver = None
    profile_data = None
    email = None
    chosen_csv_row_data = None

    try:
        with counter_lock:
            if accounts_created_count >= ACCOUNTS_TO_CREATE:
                print(f"Worker {worker_id}: Target account count reached. Exiting.")
                return

        profile_data = scrap_person_data(user_list)
        if profile_data is None:
            print(f"Worker {worker_id}: Failed to scrap person data. Exiting.")
            return

        chosen_csv_row_data = profile_data.get("chosen_csv_row")

        driver = create_driver(headless=HEADLESS)
        if not driver:
            print(f"Worker {worker_id}: Failed to create WebDriver. Exiting.")
            if chosen_csv_row_data:
                with csv_lock: user_list.append(chosen_csv_row_data)
            return

        wait = WebDriverWait(driver, 40)
        try:
            pin_img_url = get_img(
             profile_data['name'],
             profile_data['identity'],
             profile_data['use_pinterest_identity_search'],
             profile_data['original_gender']
        )[0]
        except Exception as e:
            print("Error here",e)
            pin_img_url = pinterest_scrape(
                driver,
                profile_data['name'],
                profile_data['identity'],
                profile_data['use_pinterest_identity_search'],
                profile_data['original_gender']
            )
        if pin_img_url:
             profile_data['avatar_url'] = random.choices(
                 [pin_img_url, ""], [0.9, 0.1]
             )[0]
        else:
             profile_data['avatar_url'] = ""
             print(f"Worker {worker_id}: No Pinterest image obtained.")

        bio_input = profile_data['identity']
        if profile_data.get('pronouns'):
             bio_input += f" ({profile_data['pronouns']})"

        generated_bio = get_bio(input1=bio_input.strip())
        profile_data['bio'] = random.choices([generated_bio, ""], [0.75, 0.25])[0]

        email_result = get_mail_and_code(driver, wait, get_code=False)
        if email_result is None:
             print(f"Worker {worker_id}: Failed to get email. Exiting.")
             raise Exception("Email acquisition failed")
        email, mail_window, circle_window = email_result

        password = generate_password()

        api_ids = create_person_api(email, password, profile_data)
        if api_ids is None:
            print(f"Worker {worker_id}: Failed to create person via API for {email}. Exiting.")
            raise Exception("API creation failed")

        cookies = activate_user_selenium(driver, wait, email, password, mail_window, circle_window)
        if cookies is None:
            print(f"Worker {worker_id}: Failed to activate user {email}. Exiting.")
            raise Exception("Selenium activation failed")

        db_success = insert_user_db(profile_data, email, password, api_ids, cookies)
        if not db_success:
            print(f"Worker {worker_id}: Failed to insert user {email} into database. Exiting.")
            raise Exception("Database insertion failed")


    except Exception as e:
        print(f"Worker {worker_id}: An error occurred: {e}")
        if profile_data and chosen_csv_row_data:
            if "Successfully created" not in str(e) and "Database insertion failed" not in str(e):
                 try:
                     with csv_lock:
                         user_list.append(chosen_csv_row_data)
                         print(f"Worker {worker_id}: Added user {profile_data.get('name', 'N/A')} back to the list due to failure.")
                 except Exception as add_back_e:
                      print(f"Worker {worker_id}: Error adding user back to list: {add_back_e}")

    finally:
        if driver:
            try:
                print(f"Worker {worker_id}: Quitting WebDriver instance.")
                driver.quit()
            except Exception as qe:
                print(f"Worker {worker_id}: Error quitting WebDriver: {qe}")
        print(f"Worker {worker_id}: Finished.")
        

if __name__ == "__main__":
    NUM_THREADS = int(input("Enter the amount of Threads\n"))
    ACCOUNTS_TO_CREATE = int(input("Enter the amount of accounts you want to create\n"))
    WARP = bool(input("Activate Warp? Leave empty if no\n"))
    HEADLESS = bool(input("Run headless? leave empty if no\n"))
    if WARP:
        print("f")
        restart_warp()
    while True:
        kill_chrome_and_driver()
        if accounts_created_count >= ACCOUNTS_TO_CREATE:
            print(f'Total accounts created: {accounts_created_count}')
            break
        print("Starting account creation script...")

        master_user_list = read_all_users_from_csv()

        if master_user_list is None or not master_user_list:
            print("Exiting: Could not load users from CSV or list is empty.")
            exit()

        print(f"Target: Create {accounts_created_count}/{ACCOUNTS_TO_CREATE} accounts using {NUM_THREADS} threads.")

        threads = []
        shared_scraper = cloudscraper.create_scraper()

        for i in range(NUM_THREADS):
            with counter_lock:
                if accounts_created_count >= ACCOUNTS_TO_CREATE:
                    print("Target count reached before starting all threads.")
                    break

            worker_id = i + 1
            thread = threading.Thread(
                target=account_creation_worker,
                args=(worker_id, master_user_list)
            )
            threads.append(thread)
            thread.start()
            time.sleep(random.uniform(1, 3))
        for thread in threads:
            thread.join()

        print("-" * 30)
        print(f"All worker threads have completed.")
        print(f"Total accounts created in this run: {accounts_created_count}")

        if master_user_list is not None:
            print("Rewriting CSV file with remaining users...")
            rewrite_csv(master_user_list)
        else:
            print("Skipping CSV rewrite as master list was not loaded.")

        try:
            if db_cursor: db_cursor.close()
            if db_conn: db_conn.close()
            print("Database connection closed.")
        except Exception as e:
           # print(f"Error closing database connection: {e}")
           pass

        print("Script finished.")