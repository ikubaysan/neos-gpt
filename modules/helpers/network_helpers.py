import requests
from PIL import Image
from io import BytesIO
from typing import Union
import base64
from typing import Optional

def get_image_from_url(url: str) -> Union[Image.Image, None]:
    try:
        response = requests.get(url)
        response.raise_for_status()  # Ensure the request was successful
        image = Image.open(BytesIO(response.content))
        return image
    except Exception as e:
        print(f"An error occurred: {e}")
        return None



def get_base64_from_image_url(url: str) -> Optional[str]:
    image = get_image_from_url(url)
    if image is None:
        return None

    buffered = BytesIO()
    image.save(buffered, format=image.format)
    img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
    return img_base64
