import scrapy


class InstagramItem(scrapy.Item):
    source_user = scrapy.Field()
    name = scrapy.Field()
    user_id = scrapy.Field()
    photo = scrapy.Field()
    status = scrapy.Field()
    _id = scrapy.Field()
