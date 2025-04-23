def get_cookies(driver, x, y):
    cookies = driver.get_cookies()

    for cookie in cookies:
        if cookie['name'] == x:
            remember_user_token = cookie['value']
        elif cookie['name'] == y:
            user_session_identifier = cookie['value']
    return remember_user_token, user_session_identifier