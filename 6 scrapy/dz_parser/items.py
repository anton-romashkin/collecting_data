# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class DzParserItem(scrapy.Item):
    name = scrapy.Field()
    link = scrapy.Field()
    author = scrapy.Field()
    price_regular = scrapy.Field()
    price_discount = scrapy.Field()
    price_no_discount = scrapy.Field()
    rating = scrapy.Field()
    _id = scrapy.Field()
