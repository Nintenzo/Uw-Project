from datetime import datetime, timedelta

def sleep_until_4am(isprint=False):
    now = datetime.now()
    today_4am = now.replace(hour=4, minute=0, second=0, microsecond=0)

    if now > today_4am:
        target = today_4am + timedelta(days=1)
    else:
        target = today_4am

    sleep_seconds = (target - now).total_seconds()
    if sleep_seconds > 0:
        if isprint:
            print(f"Current time is {now}. Sleeping for {sleep_seconds} seconds until {target}...")
        return sleep_seconds + 10
        
    else:
        if isprint:
            print(f"Current time is {now}. It's already past 04:00, starting schedule immediately.")
        return 10