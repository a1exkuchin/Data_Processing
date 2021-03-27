# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader.processors import Compose, TakeFirst


def parse_params(params):
    string = '*'.join([i.replace('\n', '').strip().replace('  ', '') for i in params])
    array = string.strip('*').split('***')
    result = dict()
    for elem in array:
        key, value = elem.split('**')
        result[key] = value
    print(result)
    return result

class FotoparserItem(scrapy.Item):
    name = scrapy.Field(output_processor=TakeFirst())
    photos = scrapy.Field()
    url = scrapy.Field(output_processor=TakeFirst())
    _id = scrapy.Field()
    params = scrapy.Field(output_processor=Compose(parse_params))
    price = scrapy.Field(output_processor=TakeFirst())
