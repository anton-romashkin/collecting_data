from pymongo import MongoClient


class IgSubsPipeline:
    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.mongo_base = client.instagram

    def process_item(self, item, spider):
        collection = self.mongo_base[spider.name]
        collection.update_one(item, {'$set': item}, upsert=True)
        return item
