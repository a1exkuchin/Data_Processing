# -*- coding: utf-8 -*-
# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from itemadapter import ItemAdapter
from pymongo import MongoClient

MONGO_URL = 'localhost:27017'
MONGO_DB = 'vacancy'

class JobparserPipeline:
    def __init__(self):
        self.client = MongoClient(MONGO_URL)
        self.mongo_base = self.client[MONGO_DB]

    def process_item(self, item, spider):
        if spider.name == 'superjob_ru':
            item['salary'] = self.salary_parse_superjob(item['salary'])
        elif spider.name == 'hh_ru':
            item['salary'] = self.salary_parse_hh(item['salary'])
        
        vacancy_name = ''.join(item['name'])

        salary_min = item['salary'][0]
        salary_max = item['salary'][1]
        salary_currency = item['salary'][2]
        vacancy_link = item['vacancy_link']
        site_scraping = item['site_scraping']

        vacancy_data = {
            'vacancy_name': vacancy_name, 
            'salary_min': salary_min, 
            'salary_max': salary_max, 
            'salary_currency': salary_currency, 
            'vacancy_link': vacancy_link, 
            'site_scraping': site_scraping
        }
        
        collection = self.mongo_base[spider.name]
        collection.update_one(vacancy_data, {"$set": vacancy_data}, upsert=True)
        return vacancy_data
    
    
    def salary_parse_hh(self, salary):
        salary_min = None
        salary_max = None
        salary_currency = None
        
        for i in range(len(salary)):
            salary[i] = salary[i].replace(u'\xa0', u'')
        if salary[0] == 'до':
            salary_max = salary[1]
            salary_currency = salary[-2]
        elif salary[0] == 'от':
            salary_min = salary[1]
            salary_currency = salary[-2]
        elif len(salary) == 7:
            salary_min = salary[1]
            salary_max = salary[3]
            salary_currency = salary[-2]
        return [salary_min, salary_max, salary_currency]            


    def salary_parse_superjob(self, salary):
        salary_min = None
        salary_max = None
        salary_currency = None

        for i in range(len(salary)):
            salary[i] = salary[i].replace(u'\xa0', u'')
        if salary[0] == 'до':
            salary_max = salary[2][:-4]
            salary_currency = salary[2][-4:]
        elif len(salary) == 5 and salary[0].isdigit():
            salary_max = salary[0]
        elif salary[0] == 'от':
            salary_min = salary[2][:-4]
            salary_currency = salary[2][-4:]
        elif len(salary) > 5 and salary[0].isdigit():
            salary_min = salary[0]
            salary_max = salary[4]
            salary_currency = salary[-3]

        return [salary_min, salary_max, salary_currency]




