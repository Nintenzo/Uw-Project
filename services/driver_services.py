from seleniumbase import Driver

def create_driver():
    global driver
    driver = Driver(uc=True, incognito=True, headless=False, no_sandbox=True, disable_gpu=True)
    return driver