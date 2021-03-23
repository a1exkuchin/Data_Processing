import scrapy


class SuperjobRuSpider(scrapy.Spider):
    name = 'superjob_ru'
    allowed_domains = ['superjob.ru']
    start_urls = ['http://superjob.ru/']

    def parse(self, response):
        pass
