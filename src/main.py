from src.scraper.image_scraper import ImageScraper


if __name__ == '__main__':
    scraper = ImageScraper()
    urls = scraper.fetch_image_urls('Dogs', 1, 2)
    for url in urls:
        scraper.persist_image('/Users/rajanchauhan/Desktop/Programming-Projects.nosync/Python '
                          'Projects/image-scraper/images', url)