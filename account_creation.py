import requests
import time
import random
import string
import os
from PIL import Image
from imgurpython import ImgurClient
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from seleniumbase import Driver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import gender_guesser.detector as gender
import re
from selenium.webdriver.common.by import By
import sqlite3

full_names = [
    "Thomas Davis", "Richard Garcia", "Melissa Miller", "Charles White", "Melissa Garcia",
    "Michael Roberts", "Shirley Anderson", "Elizabeth Thompson", "Richard Moore", "Patricia Jones",
    "David Johnson", "Jessica Williams", "Sarah Brown", "James Wilson", "Maria Martinez",
    "John Taylor", "Emily Thomas", "Linda Lee", "William Harris", "Barbara Clark",
    "Joshua Lewis", "Karen Young", "Paul Hall", "Laura Allen", "Andrew Scott",
    "Nancy Adams", "Joseph King", "Rebecca Wright", "Henry Green", "Helen Lopez",
    "Robert Hill", "Margaret Walker", "Daniel Baker", "Lisa Nelson", "Kevin Carter",
    "Carol Perez", "Jack Mitchell", "Jessica Roberts", "Steven Collins", "Kimberly Edwards",
    "Gary Stewart", "Deborah Morris", "Matthew Rogers", "Betty Reed", "Benjamin Cooper",
    "Christine Morgan", "Steven Ward", "Virginia Bell", "Mark Bryant", "Cynthia Murphy",
    "Brian Cox", "Patricia Rivera", "George Ward", "Dorothy Russell", "Keith Foster",
    "Lori Jenkins", "Frank Simmons", "Nancy Thomas", "John Murphy", "Rachel Scott",
    "Eleanor Peterson", "Eric Price", "Theresa Bennett", "David Parker", "Pamela Rogers",
    "Jacob Ward", "Linda Allen", "Jackie Green", "Edward Jenkins", "Grace Sanchez",
    "Jonathan Carter", "Ruth Clark", "Kevin Phillips", "Amanda Robinson", "Christopher Hill",
    "Diane Butler", "Alice Perez", "Samuel Young", "Nancy Bennett", "Brandon Foster",
    "Megan Gonzalez", "Jason King", "Martha Smith", "Joseph Baker", "Pamela Price",
    "Matthew Clark", "Sophia Cook", "Alexander Collins", "Stephanie Morris", "Sarah Thompson",
    "Deborah Bailey", "Timothy Hughes", "Karen Reed", "Lori Robinson", "Samuel Allen",
    "Zachary Baker", "Patricia Williams", "George Anderson", "Ann Gonzalez", "Brian Lewis",
    "Emma Stewart", "Jack Taylor", "Sophia Green", "Michael Clark", "William Campbell",
    "Patricia Young", "Helen Ross", "James Scott", "Emily Wright", "Steven Johnson",
    "Joshua Martinez", "Ethan Hill", "Sarah Price", "William Bennett", "Jessica Reed",
    "James Moore", "Deborah Moore", "Andrew Thomas", "Michael Davis", "Evelyn Rogers",
    "Joseph Adams", "Angela Taylor", "Joseph Young", "Jonathan Williams", "Christopher Harris",
    "Deborah Clark", "Shirley Martinez", "Margaret Hill", "Zachary Clark", "Virginia Thomas",
    "David Lewis", "Helen Adams", "Megan Hall", "Matthew Johnson", "Katherine Ross",
    "Lori Davis", "Diana Clark", "Timothy Phillips", "Steven Carter", "Benjamin Mitchell",
    "Catherine Roberts", "Joseph Lee", "Sarah Martin", "Susan Green", "Cynthia Johnson",
    "Frank Green", "Patricia White", "Emma Foster", "Benjamin Brown", "Gary Mitchell",
    "Sandra Harris", "Deborah Young", "Michael Johnson", "William Green", "Susan Taylor",
    "Rachel Lewis", "Sarah Foster", "Nancy Walker", "Ethan Johnson", "Angela Parker",
    "Jacob Allen", "Linda Thomas", "Michael Moore", "Shannon Martin", "James Taylor",
    "Rachel Young", "Catherine Lewis", "Christopher Green", "Emma Mitchell", "Megan Carter",
    "David Young", "Andrew Davis", "William Stewart", "Diane Ross", "Kevin Martin",
    "Mary Anderson", "Emily Gonzalez", "Linda Scott", "David Wright", "Stephanie Johnson",
    "Elizabeth Taylor", "Joshua Martin", "Jacob White", "Kimberly Davis", "Helen King",
    "Brian Walker", "Deborah Gonzalez", "Matthew Taylor", "Megan Baker", "Michael Ward",
    "David Thomas", "Emily Brown", "Sarah Harris", "Patricia Green", "Ethan Moore",
    "Megan Roberts", "Joseph Green", "Shannon Taylor", "James Johnson", "Susan Williams",
    "Catherine Mitchell", "Timothy Martin", "Deborah Green", "Jessica Harris", "Joseph Hill",
    "Martha Mitchell", "Barbara White", "Samuel Brown", "Jessica Harris", "Diana Walker",
    "Edward Harris", "Joshua White", "Elizabeth Walker", "Benjamin Green", "William Mitchell",
    "Jacob Gonzalez", "Emma White", "Rachel Taylor", "Susan Johnson", "Christopher Scott",
    "Shirley Walker", "Robert Brown", "Grace Harris", "Laura Martin", "Matthew Walker",
    "Andrew Mitchell", "Susan White", "Timothy Brown", "Barbara Green", "Cynthia Martin",
    "Grace Green", "John Lee", "Kevin White", "Matthew Harris", "Karen Thomas",
    "Joseph Moore", "Shannon Green", "Ethan Brown", "Deborah Harris", "Joseph Green",
    "Martha Taylor", "William Taylor", "Linda Harris", "Catherine Walker", "Michael Green",
    "Timothy Lewis", "Emma Lewis", "Evelyn Johnson", "Christopher Brown", "Timothy Reed",
    "Rachel Harris", "Steven Brown", "Shirley Taylor", "Catherine Harris", "Megan White",
    "William White", "Jessica Johnson", "Deborah Brown", "Zachary Green", "Jonathan White",
    "Andrew Harris", "Emma Brown", "George Green", "Helen White", "Deborah Taylor",
    "Emma Walker", "Megan Lewis", "William White", "Christopher Mitchell", "Patricia Hill",
    "Lori Green", "Thomas White", "Ethan Taylor", "George Martin", "Timothy White",
    "Barbara Harris", "Emily White", "Matthew Lewis", "Deborah White", "Zachary Lewis"
]

d = gender.Detector()

url = "https://app.circle.so/api/v1/community_members"
conn = sqlite3.connect("circle_users.db")
cursor = conn.cursor()

def create_persons():
    name = random.choice(full_names)
    sex = d.get_gender(name[0:name.index(" ")])
    while sex:
        if sex in ["male", "mostly_male"] :
            api_url = "https://this-person-does-not-exist.com/new?time=1745094902230&gender=male&age=26-35&etnic=all"
            break
        elif sex in ["female", "mostly_female"]:
            api_url = "https://this-person-does-not-exist.com/new?time=1745094902230&gender=female&age=26-35&etnic=all"
            break
        name = random.choice(full_names)
        continue
    response = requests.get(api_url)
    data = response.json()

    if not os.path.exists("persons"):
        os.makedirs("persons")
    image_src = data['src'].replace('\\', '')
    image_url = f"https://this-person-does-not-exist.com{image_src}"
    image_name = data['name']
    download_path = os.path.join("persons", image_name)

    img_data = requests.get(image_url).content
    with open(download_path, 'wb') as f:
        f.write(img_data)

    cropped_path = download_path.replace(".jpg", "_cropped.jpg")
    with Image.open(download_path) as img:
        width, height = img.size
        cropped = img.crop((0, 60, width, height - 60))
        cropped.save(cropped_path)

    client_id = 'b4c533826633a63'
    client_secret = 'dffc6142394eed90f22960d0c9c25a8d85cdbe86'
    client = ImgurClient(client_id, client_secret)

    uploaded = client.upload_from_path(cropped_path, config=None, anon=True)
    return name, uploaded['link']

def create_db():
    global cursor, conn
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,        
        email TEXT NOT NULL,
        password TEXT
    )
    """)

def insert_users(name, email, password):
    global cursor, conn
    try:
        # Insert data into the posts table
        cursor.execute("""
        INSERT INTO users (name, email, password)
        VALUES (?, ?, ?)
        """, (name,email, password))
        conn.commit()  # Commit the transaction
        print("Data inserted successfully!")
    except sqlite3.Error as e:
        print(f"Error inserting data: {e}")
        
def create_driver():
    global driver
    driver = Driver(uc=True, incognito=True, headless=False)
    return driver

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

def login(email,pw):
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
                driver.quit()
                return
    time.sleep(55)
create_db()
while True:
    fullname,image = create_persons()
    mailstring = get_mail(x="mail")
    pw = generate_password()
    insert_users(fullname,mailstring,pw)
    payload = {
        "email": mailstring,
        "password": pw,
        "name": fullname,
        "avatar": image,
        "community_id": "337793",
        "space_ids": [1987412],
        "skip_invitation": False,
    }
    headers = {
    'Authorization': f'Token ceLDhha7NKK6QMY2LU79B6EPc7LuUfrz'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    print(response.status_code)
    print(response.text)
    login(email=mailstring,pw=pw)
    time.sleep(1)