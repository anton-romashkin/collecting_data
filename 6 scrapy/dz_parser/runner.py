from scrapy.settings import Settings
from scrapy.crawler import CrawlerProcess

from dz_parser import settings
from dz_parser.spiders.labirint import LabirintSpider
from dz_parser.spiders.book24 import Book24Spider

if __name__ == '__main__':
    labirint_settings = Settings()
    labirint_settings.setmodule(settings)

    process = CrawlerProcess(settings=labirint_settings)
    process.crawl(LabirintSpider)
    process.crawl(Book24Spider)

    process.start()
