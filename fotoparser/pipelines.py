# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import scrapy
import os
from urllib.parse import urlparse
from scrapy.pipelines.images import ImagesPipeline
from pymongo import MongoClient


class FotoparserPipeline(ImagesPipeline):
    def file_path(self, request, response=None, info=None, *, item=None):
        file = os.path.basename(urlparse(request.url).path)
        path = file[:-4].split('_')[0] + '/'
        return path + file

    def get_media_requests(self, item, info):
        if item["photos"]:
            for photo_url in item['photos']:
                try:
                    yield scrapy.Request(photo_url)
                except Exception as e:
                    print(e)

    def item_completed(self, results, item, info):
        if results:
            item["photos"] = [itm[1] for itm in results]
        return item


class DataBasePipeline:
    def __init__(self):
        MONGO_URL = 'mongodb://127.0.0.1:27017/'
        MONGO_DB = 'fotoparse'

        client = MongoClient(MONGO_URL)
        self.mongo_db = client[MONGO_DB]

    def process_item(self, item, spider):
        collection = self.mongo_db[spider.name]
        collection.update_one(item, {"$set": item}, upsert=True)
        return item
