# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from pymongo import MongoClient


class InstaparserPipeline:
    def process_item(self, item, spider):
        return item

class DataBasePipeline:
    def __init__(self):
        MONGO_URL = 'mongodb://127.0.0.1:27017/'
        MONGO_DB = 'socialnet'

        client = MongoClient(MONGO_URL)
        self.mongo_db = client[MONGO_DB]

    def process_item(self, item, spider):
        collection = self.mongo_db[spider.name]
        collection.update_one(item, {"$set": item}, upsert=True)
        return item