import hashlib
import io
import logging
import os
import time
import requests
from selenium import webdriver
from PIL import Image

logging.basicConfig(format='%(asctime)s %(levelname)s %(process)d --- %(name)s %(funcName)20s() : %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S', level=logging.INFO)


class ImageScraper:
    logger = logging.getLogger('ImageScraper')

    def __init__(self):
        self.driver = webdriver.Chrome()

    def get_image_urls(self, query: str, max_urls: int, sleep_between_interactions: int = 1):
        search_url = "https://www.google.com/search?safe=off&site=&tbm=isch&source=hp&q={q}&oq={q}&gs_l=img"
        self.driver.get(search_url.format(q=query))

        image_urls = set()
        image_count = 0
        results_start = 0
        while image_count < max_urls:
            self.__scroll_to_end(sleep_between_interactions)
            thumbnail_results = self.driver.find_elements_by_css_selector("img.Q4LuWd")
            number_results = len(thumbnail_results)
            self.logger.info(f"Found: {number_results} search results. Extracting links from {results_start}:{number_results}")

            for img in thumbnail_results[results_start:number_results]:
                self.__click_and_wait(img, sleep_between_interactions)
                self.__add_image_urls_to_set(image_urls)
                image_count = len(image_urls)
                if image_count >= max_urls:
                    self.logger.info(f"Found: {len(image_urls)} image links, done!")
                    break
            else:
                self.logger.info(f"Found: {len(image_urls)} image links, looking for more ...")

                load_more_button = self.driver.find_element_by_css_selector(".mye4qd")
                if load_more_button:
                    self.logger.info("loading more...")
                    self.driver.execute_script("document.querySelector('.mye4qd').click();")

            # move the result startpoint further down
            results_start = len(thumbnail_results)

        return image_urls

    def persist_image(self, folder_path: str, url: str):
        image_content = self.__download_image_content(url)
        try:
            image_file = io.BytesIO(image_content)
            image = Image.open(image_file).convert('RGB')
            file_path = os.path.join(folder_path, hashlib.sha1(image_content).hexdigest()[:10] + '.jpg')
            with open(file_path, 'wb') as f:
                image.save(f, "JPEG", quality=85)
            self.logger.info(f"SUCCESS - saved {url} - as {file_path}")
        except Exception as e:
            self.logger.error(f"ERROR - Could not save {url} - {e}")

    def get_in_memory_image(self, url: str, format: str):
        image_content = self.__download_image_content(url)
        try:
            image_file = io.BytesIO(image_content)
            pil_image = Image.open(image_file).convert('RGB')
            in_mem_file = io.BytesIO()
            pil_image.save(in_mem_file, format=format)
            return in_mem_file.getvalue()
        except Exception as e:
            self.logger.error(f"Could not get image data: {e}")

    def close_connection(self):
        self.driver.quit()

    def __download_image_content(self, url):
        try:
            return requests.get(url).content
        except Exception as e:
            self.logger.error(f"ERROR - Could not download {url} - {e}")

    def __scroll_to_end(self, sleep_time):
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(sleep_time)

    def __click_and_wait(self, img, wait_time):
        try:
            img.click()
            time.sleep(wait_time)
        except Exception:
            return

    def __add_image_urls_to_set(self, image_urls: set):
        actual_images = self.driver.find_elements_by_css_selector('img.n3VNCb')
        for actual_image in actual_images:
            if actual_image.get_attribute('src') and 'http' in actual_image.get_attribute('src'):
                image_urls.add(actual_image.get_attribute('src'))
