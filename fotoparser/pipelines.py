# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import scrapy
#from itemadapter import ItemAdapter
from scrapy.pipelines.images import ImagesPipeline
from pymongo import MongoClient


class FotoparserPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        # print(item["photos"])
        print(item)
        if item["photos"]:
            for photo_url in item['photos']:
                try:
                    yield scrapy.Request(photo_url)
                except Exception as e:
                    print(e)

    def item_completed(self, results, item, info):

        print(results)

        if results:
            item["photos"] = [itm[1] for itm in results]
        return item


class DataBasePipeline:
    def __init__(self):
        MONGO_URL = 'mongodb://127.0.0.1:27017/'
        MONGO_DB = 'leroymerlin'

        client = MongoClient(MONGO_URL)
        self.mongo_db = client[MONGO_DB]

    def process_item(self, item, spider):
        collection = self.mongo_db[spider.name]
        collection.insert_one(item)
        collection.update_one(item, {"$set": item}, upsert=True)
        return item
