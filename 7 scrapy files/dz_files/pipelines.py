from scrapy.pipelines.images import ImagesPipeline
from pymongo import MongoClient
import scrapy


class DzFilesPipeline:
    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.mongo_base = client.merlen

    def process_item(self, item, spider):
        item['specs'] = self.format_specs(item['specs_keys'], item['specs_values'])
        del item['specs_keys'], item['specs_values']

        collection = self.mongo_base[spider.name]
        collection.update_one(item, {'$set': item}, upsert=True)
        return item

    def format_specs(self, keys, values):
        return dict(zip(keys, values))


class MerlenPicturesPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        n = 1
        if item['images']:
            for img in item['images']:
                try:
                    yield scrapy.Request(img, meta={
                        'name': item['name'],
                        'file': n
                    })
                    n += 1

                except Exception as e:
                    print(e)

    def item_completed(self, results, item, info):
        item['images'] = [itm[1] for itm in results if itm[0]]
        return item

    def file_path(self, request, response=None, info=None):
        path = f"{request.meta['name']}/{request.meta['file']}.jpg"
        return path
