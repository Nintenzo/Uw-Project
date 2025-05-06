def get_cookies(driver, x):
    cookies = driver.get_cookies()
    cookies_list = []
    for cookie in cookies:
        if cookie['name'] in x:
            cookies_list.append(cookie['value'])
    return cookies_list
