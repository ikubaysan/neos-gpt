import requests
from PIL import Image
from io import BytesIO
from typing import Union

def get_image_from_url(url: str) -> Union[Image.Image, None]:
    try:
        response = requests.get(url)
        response.raise_for_status()  # Ensure the request was successful
        image = Image.open(BytesIO(response.content))
        return image
    except Exception as e:
        print(f"An error occurred: {e}")
        return None