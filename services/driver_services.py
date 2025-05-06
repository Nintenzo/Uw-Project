from seleniumbase import Driver

def create_driver(headless=True):
    global driver
    driver = Driver(uc=True, incognito=True, headless=headless, no_sandbox=True, disable_gpu=True, page_load_strategy="eager")
    return driver