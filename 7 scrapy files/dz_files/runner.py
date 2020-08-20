from scrapy.settings import Settings
from scrapy.crawler import CrawlerProcess

from dz_files import settings
from dz_files.spiders.merlen import MerlenSpider

if __name__ == '__main__':
    merlen_settings = Settings()
    merlen_settings.setmodule(settings)

    process = CrawlerProcess(settings=merlen_settings)
    process.crawl(MerlenSpider)

    process.start()
