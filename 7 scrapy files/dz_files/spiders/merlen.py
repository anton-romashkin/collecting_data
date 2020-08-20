import scrapy
from scrapy.http import HtmlResponse
from scrapy.loader import ItemLoader
from dz_files.items import DzFilesItem


# https://leroymerlin.ru/catalogue/cirkulyarnye-pily/

class MerlenSpider(scrapy.Spider):
    name = 'merlen'
    allowed_domains = ['leroymerlin.ru']
    start_urls = ['https://leroymerlin.ru/catalogue/cirkulyarnye-pily/']

    def parse(self, response: HtmlResponse):
        prod_links = response.xpath("//a[@slot='name']")

        for link in prod_links:
            yield response.follow(link, callback=self.prod_parse)
            next_page = response.xpath(
                "//div[@class='next-paginator-button-wrapper']/a/@href").extract_first()
            if next_page:
                yield response.follow(next_page, callback=self.parse)

    def prod_parse(self, response: HtmlResponse):
        loader = ItemLoader(item=DzFilesItem(), response=response)
        loader.add_xpath('name', "//h1/text()")
        loader.add_value('link', response.url)
        loader.add_xpath('images', "//picture[@slot='pictures']/img/@src")
        loader.add_xpath('price', "//span[@slot='price']/text()")
        loader.add_xpath('specs_keys', "//dt/text()")
        loader.add_xpath('specs_values', "//dd/text()")
        yield loader.load_item()
