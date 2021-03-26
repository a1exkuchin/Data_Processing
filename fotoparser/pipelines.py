# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import scrapy
from itemadapter import ItemAdapter
from scrapy.pipelines.images import ImagesPipeline

class FotoparserPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        #print(item["photos"])
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
        print('Photoparser is work')
        return item

class DataBasePipeline:
    def process_item(self, item, spider):
        # TODO: save data to MongoDB!
        #print('Write data is work')
        return item
