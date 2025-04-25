from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from services.cookies_service import get_cookies
from services.db_service import get_user_cookies, get_user_password, update_cookies
from services.driver_services import create_driver
from selenium.webdriver.support.ui import WebDriverWait
import requests
import time

def last_seen(email):
    try:
        cookies = get_user_cookies(email)
        remember_user_token = cookies[0][0]
        user_session_identifier = cookies[0][1]
        url = "https://tubiit.circle.so/feed"
        cookies = {
            "remember_user_token": remember_user_token,
            "user_session_identifier": user_session_identifier,
        }
        try:
            requests.get(url, cookies=cookies)
        except Exception:
            time.sleep(10)
            requests.get(url, cookies=cookies)
        time.sleep(2)
        print("last seen mimicked")
        return
    except Exception:
        selenium_seen(email)


def selenium_seen(email):
    driver = create_driver()
    wait = WebDriverWait(driver, 60)
    pw = get_user_password(email)[0]
    driver.get("https://login.circle.so/sign_in?request_host=app.circle.so#email")
    emailform = wait.until(EC.visibility_of_element_located((By.NAME, "user[email]")))
    emailform.send_keys(email)
    password = wait.until(EC.visibility_of_element_located((By.NAME, "user[password]")))
    password.send_keys(pw)
    password.send_keys(Keys.ENTER)
    while True:
        current_url = driver.current_url
        if current_url == "https://tubiit.circle.so/feed":
            remember_user_token, user_session_identifier = get_cookies(driver, "remember_user_token","user_session_identifier")
            driver.quit()
            print("last seen mimicked")
            update_cookies(remember_user_token, user_session_identifier, email)
            return
        time.sleep(0.5)
