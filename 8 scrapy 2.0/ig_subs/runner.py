from scrapy.settings import Settings
from scrapy.crawler import CrawlerProcess

from ig_subs import settings
from ig_subs.spiders.instagram import InstagramSpider

if __name__ == '__main__':
    ig_settings = Settings()
    ig_settings.setmodule(settings)

    process = CrawlerProcess(settings=ig_settings)
    process.crawl(InstagramSpider)

    process.start()
