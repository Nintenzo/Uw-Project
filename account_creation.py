import requests
import re
import time
import random
import csv
import os
import string
import cloudscraper
from services.warp_service import restart_warp
from services.db_service import create_db_users, insert_users, fetch_spaces_id
from settings.cities import uscities
from settings.bio_keywords import bio_words
from services.pinterest_api import get_img
from identity_data import LGBT_IDENTITIES, get_pronouns
from activator_service import send_otp
from services.create_email import create_email
from dotenv import load_dotenv

load_dotenv()
csv.field_size_limit(3828443) 
scraper = cloudscraper.create_scraper()
url = "https://app.circle.so/api/v1/community_members"
community_id = os.getenv("COMMUNITY_ID")
spaces = fetch_spaces_id("space_id").fetchall()
space = []
all_rows_read = []
chosen_row_index_in_original = None
csv_filepath = 'users.csv'
for x in spaces:
    space.append(x[0])
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
             #print(f"Warning: IndexError during username manipulation ('{op}' on '{''.join(current_username_list)}'). Skipping change.")
             continue
    modified_username = "".join(current_username_list)
    if modified_username == original_username:
        modified_username += str(random.randint(0, 9))
        if modified_username == original_username:
             return original_username + "_mod"

    return modified_username

def get_bio(input1):
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
    request = requests.get(url, data=payload)
    request = request.json()
    return request.get('results')[random.randint(1,2)][3:]


def get_username(target_identity, original_gender):
    """Gets a name/username, filtering CSV based on target identity. If no match, tries the other gender."""
    global all_rows_read, chosen_row_index_in_original
    selected_final_value = None
    chosen_csv_gender = None
    pin = False
    all_rows_read = []
    

    def filter_rows(target_identity_cap, original_gender_cap):
        filtered = []
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
                if original_gender_cap == "Female" and csv_gender == "Male":
                    match = True
                elif original_gender_cap == "Male" and csv_gender == "Female":
                    match = True
            if match:
                filtered.append(row)
        return filtered

    try:
        if os.path.exists(csv_filepath):
            with open(csv_filepath, 'r', newline='', encoding='utf-8') as f:
                reader = csv.reader(f)
                all_rows_read = [row for row in reader if len(row) >= 3 and all(c.strip() for c in row[:3])]

            target_identity_cap = target_identity.capitalize()
            original_gender_cap = original_gender.capitalize() if original_gender else None
            filtered_rows = filter_rows(target_identity_cap, original_gender_cap)

            # If no match, try the other gender
            if not filtered_rows and target_identity_cap in ["Male", "Gay", "Female", "Lesbian"]:
                alt_identity = "Female" if target_identity_cap in ["Male", "Gay"] else "Male"
                filtered_rows = filter_rows(alt_identity, original_gender_cap)
                if filtered_rows:
                    #print(f"No rows for {target_identity_cap}, falling back to {alt_identity}.")
                    target_identity_cap = alt_identity

            if filtered_rows:
                chosen_row = random.choice(filtered_rows)
                chosen_row_index_in_original = all_rows_read.index(chosen_row)
                username = chosen_row[0].strip()
                name = chosen_row[1].strip()
                chosen_csv_gender = chosen_row[2].strip()
                if random.choice([True, False]):
                    selected_final_value = manipulate_username(username)
                    pin = False
                    #print(f"Using manipulated username from CSV: {selected_final_value}")
                else:
                    selected_final_value = name
                    pin = True
                    #print(f"Using full name from CSV: {selected_final_value}")
            else:
                pass
                #print(f"Warning: No CSV rows match target identity '{target_identity}' or fallback gender.")
        else:
            pass
            #print(f"Warning: {csv_filepath} not found.")
    except Exception as e:
        pass
        #print(f"Error processing {csv_filepath}: {e}")
    return [selected_final_value, chosen_csv_gender, pin]



def delete_row_from_csv(all_rows_read, chosen_row_index_in_original):
    """Deletes the selected row from the list and updates the CSV file."""
    del all_rows_read[chosen_row_index_in_original]
    with open(csv_filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(all_rows_read)
        print(f"Deleted row {chosen_row_index_in_original} from {csv_filepath}.")
    return

def get_job(scraper):
    while True:
        url = "https://writingexercises.co.uk/php_WE/job.php?_=1745167420134"
        job = scraper.get(url)
        if job.text == "Fisherman/woman":
            continue
        return randomize_first_letter_case(job.text)

def scrap_person_data():
    global final_identity, original_gender
    try:
        headline = get_job(scraper)
        original_gender = random.choice(["male","female"])
        final_identity = original_gender
        pronouns = None
        if random.randint(1, 100) <= 9.3:
            final_identity = random.choice(LGBT_IDENTITIES)
            pronouns = get_pronouns(final_identity, original_gender)
            #print(f"Selected LGBT Identity: {final_identity}, Pronouns: {pronouns}")
        else:
            final_identity = original_gender
            #print(f"Selected Identity: {final_identity}")

        # --- Username and Name Selection (using get_username) ---
        username_data = get_username(final_identity, original_gender)
        final_name_or_username = username_data[0]
        use_pin_search_modifier_from_csv = username_data[2]
        job_title_input = ["", headline]
        job_title_input = random.choice(job_title_input)

        # --- Determine final Pinterest search modifier ---
        if final_identity in LGBT_IDENTITIES:
            add_term_to_pinterest_search = True # Force add for LGBT
            #print("Forcing Pinterest identity search for LGBT identity.")
        else:
            # For Male/Female, respect the boolean from get_username
            add_term_to_pinterest_search = use_pin_search_modifier_from_csv
            #print(f"Pinterest identity search for Male/Female determined by CSV logic: {add_term_to_pinterest_search}")

        # --- Image Selection ---
        pin_img, bio_modifier = get_img(final_name_or_username, final_identity, add_term_to_pinterest_search, original_gender)


        if final_identity in LGBT_IDENTITIES:
            #print(final_identity)
            #print(pronouns)
            selected_bio = get_bio(input1=f"{final_identity} {pronouns} {bio_modifier}")
        else:
            selected_bio = get_bio(input1=f"{bio_modifier}")
        final_image = random.choices([pin_img, ""], [0.9, 0.1])[0]
        selected_bio = random.choices([selected_bio, ""], [0.65, 0.35])[0]
        if random.choice([True, False]):
            city = random.choice(uscities)
        else:
            city = ""
        return final_name_or_username, original_gender, final_identity, selected_bio, job_title_input, city, final_image, pronouns

    except Exception as e:
        print("Error:", e)
        # restart_warp()

def create_person():
    try:
        payload = {
            "email": mailstring,
            "password": pw,
            "name": fullname,
            "bio": bio,
            "headline": headline,
            "avatar": avatar,
            "community_id": community_id,
            "space_ids": space,
            "skip_invitation": False,
            "location": city
        }
        headers = {'Authorization': 'Token ceLDhha7NKK6QMY2LU79B6EPc7LuUfrz'}
        try:
            response = requests.request("POST", url, headers=headers, json=payload)
        except Exception:
            time.sleep(10)
            response = requests.request("POST", url, headers=headers, json=payload)
        data = response.json()
        member_id = data.get('user').get('id')
        public_uid = data.get('user').get('public_uid')
        community_member_id = data.get('user').get('community_member_id')
        delete_row_from_csv(all_rows_read, chosen_row_index_in_original)
        return member_id, public_uid, community_member_id
    except Exception as e:
        print(e)
            


conn, cursor = create_db_users()
count = 0
accounts_to_create = int(input())
while True:
    try:
        fullname, scraped_gender, identity, bio, headline, city, avatar, pronouns = scrap_person_data()
        #print(f"Chosen Name: {fullname}, Scraped Gender: {scraped_gender}, Final Identity: {identity}")
        data = create_email()
        mailstring, pw = data['address'], data['password']
        member_id, public_uid, community_member_id = create_person()
        cookies_list = send_otp(mailstring, pw)
        remember_user_token, user_session_identifier = "", ""
        insert_users(fullname, mailstring, pw, final_identity, original_gender, pronouns, bio, headline, city, avatar, remember_user_token, user_session_identifier, member_id, public_uid, community_member_id)
        count += 1
        print(f"{count}/{accounts_to_create}")
        if count >= accounts_to_create:
            print(f"{accounts_to_create} accounts created")
            break
    except Exception as e:
        print(e)
        