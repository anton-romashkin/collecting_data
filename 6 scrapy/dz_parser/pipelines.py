from pymongo import MongoClient
import re


class DzParserPipeline:
    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.mongo_base = client.books

    def process_item(self, item, spider):
        if item['price_regular'] is None:
            item['price_regular'] = item['price_no_discount']

        if item['price_discount'] is None:
            item['price_discount'] = item['price_regular']

        item['price_regular'] = ''.join(re.findall(r'\d', item['price_regular']))
        item['price_discount'] = ''.join(re.findall(r'\d', item['price_discount']))
        del item['price_no_discount']
        collection = self.mongo_base[spider.name]
        collection.update_one(item, {'$set': item}, upsert=True)
        return item
