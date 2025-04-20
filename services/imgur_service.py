import os
from imgurpython import ImgurClient
from dotenv import load_dotenv

load_dotenv()


def imgur_uploader(scraper, image_url):
    if not os.path.exists("persons"):
        os.makedirs("persons")
    image_filename = image_url.split("/")[-1]
    image_path = os.path.join("persons", image_filename)
    with open(image_path, 'wb') as f:
        f.write(scraper.get(image_url).content)

    client = ImgurClient(os.getenv("IMGUR_CLIENT_ID"),
                         os.getenv("IMGUR_CLIENT_SECRET"))

    uploaded_image = client.upload_from_path(image_path, config=None, anon=True)
    imgur_url = uploaded_image['link']
    return imgur_url
