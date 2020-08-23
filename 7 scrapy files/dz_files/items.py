import scrapy
from itemloaders.processors import MapCompose, TakeFirst
import re


def price_format(value):
    value = ''.join(re.findall(r'\d+', value))
    try:
        return int(value)
    except ValueError:
        return value


def specs_format(value):
    value = re.sub(r'\s\s', '', value).strip()
    return value


class DzFilesItem(scrapy.Item):
    name = scrapy.Field(output_processor=TakeFirst())
    images = scrapy.Field()
    price = scrapy.Field(input_processor=MapCompose(price_format), output_processor=TakeFirst())
    specs_keys = scrapy.Field()
    specs_values = scrapy.Field(input_processor=MapCompose(specs_format))
    specs = scrapy.Field()
    link = scrapy.Field(output_processor=TakeFirst())
    __id = scrapy.Field()
