import base64
import requests


class ImageService:

    @classmethod
    def get_image_base64(cls, url):
        try:
            response = requests.get(url)
            if response.status_code == 200:
                image_data = response.content
                base64_data = base64.b64encode(image_data).decode('utf-8')

                return base64_data
            else:
                print(
                    f"Failed to fetch image. Status code: {response.status_code}")
                raise Exception(f"Failed to fetch image: {url}")
        except Exception as e:
            raise e
