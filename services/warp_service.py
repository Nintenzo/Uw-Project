import subprocess
import time


def restart_warp():
    subprocess.run(["warp-cli", "disconnect"], stdout=subprocess.DEVNULL,
                   stderr=subprocess.DEVNULL)
    subprocess.run(["warp-cli", "connect"], stdout=subprocess.DEVNULL,
                   stderr=subprocess.DEVNULL)

    result = subprocess.run(["warp-cli", "status"],
                            capture_output=True, text=True)

    output = result.stdout.strip()
    while output != "Status update: Connected":
        result = subprocess.run(["warp-cli", "status"],
                                capture_output=True, text=True)
        output = result.stdout.strip()
        time.sleep(1)
    return
