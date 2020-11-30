from flask import Blueprint
from flask import request
from src.aws import s3_service as s3s
from src.scraper.image_scraper import ImageScraper

images = Blueprint('images', __name__)


@images.route('/images', methods=['POST'])
def post_images():
    search_term = request.form.get('SearchTerm')
    num_images = int(request.form.get('NumberOfImages'))
    bucket = request.form.get("Bucket")
    key = request.form.get("Key")
    if not search_term or not num_images or not bucket or not key:
        return "BAD REQUEST 400"
    scraper = ImageScraper()
    urls = scraper.get_image_urls(query=search_term, max_urls=num_images, sleep_between_interactions=1)
    for url in urls:
        img_obj = scraper.get_in_memory_image(url, 'jpeg')
        s3s.upload_object(img_obj, bucket, key, 'jpeg')
    return "Success 200"

