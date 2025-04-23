from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from cookies_service import get_cookies
import requests
import time

def last_seen(remember_user_token, user_session_identifier):
    url = "https://tubiit.circle.so/feed"
    cookies = {
        "remember_user_token": remember_user_token,
        "user_session_identifier": user_session_identifier,
    }

    requests.get(url, cookies=cookies)
    time.sleep(2)
    print("last seen mimicked")
    return

def selenium_seen(driver,wait,email,pw):
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
            return remember_user_token, user_session_identifier
        time.sleep(0.5)
                