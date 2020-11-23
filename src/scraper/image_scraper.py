import hashlib
import io
import logging
import os
import time
import requests
from selenium import webdriver
from PIL import Image

logging.basicConfig(format='%(asctime)s %(levelname)s %(process)d --- %(name)s %(funcName)20s() : %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S',
                    level=logging.INFO)


class ImageScraper:
    logger = logging.getLogger('ImageScraper')

    def __init__(self):
        self.driver = webdriver.Chrome()

    def fetch_image_urls(self, query: str, max_links_to_fetch: int, sleep_between_interactions: int = 1):
        def scroll_to_end():
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(sleep_between_interactions)

            # build the google query

        search_url = "https://www.google.com/search?safe=off&site=&tbm=isch&source=hp&q={q}&oq={q}&gs_l=img"

        # load the page
        self.driver.get(search_url.format(q=query))

        image_urls = set()
        image_count = 0
        results_start = 0
        while image_count < max_links_to_fetch:
            scroll_to_end()

            # get all image thumbnail results
            thumbnail_results = self.driver.find_elements_by_css_selector("img.Q4LuWd")
            number_results = len(thumbnail_results)

            self.logger.info(f"Found: {number_results} search results. Extracting links from {results_start}:{number_results}")

            for img in thumbnail_results[results_start:number_results]:
                # try to click every thumbnail such that we can get the real image behind it
                try:
                    img.click()
                    time.sleep(sleep_between_interactions)
                except Exception:
                    continue

                # extract image urls
                actual_images = self.driver.find_elements_by_css_selector('img.n3VNCb')
                for actual_image in actual_images:
                    if actual_image.get_attribute('src') and 'http' in actual_image.get_attribute('src'):
                        image_urls.add(actual_image.get_attribute('src'))

                image_count = len(image_urls)

                if len(image_urls) >= max_links_to_fetch:
                    self.logger.info(f"Found: {len(image_urls)} image links, done!")
                    break
            else:
                self.logger.info("Found:", len(image_urls), "image links, looking for more ...")
                time.sleep(30)
                return
                load_more_button = self.driver.find_element_by_css_selector(".mye4qd")
                if load_more_button:
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

    def __download_image_content(self, url):
        try:
            return requests.get(url).content
        except Exception as e:
            self.logger.error(f"ERROR - Could not download {url} - {e}")
