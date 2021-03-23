from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from jobparser import settings
from jobparser.spiders.hh_ru import HhRuSpider
from jobparser.spiders.superjob_ru import SuperjobRuSpider

if __name__ == '__main__':

    crawler_settings = Settings()
    crawler_settings.setmodule(settings)
    
    process = CrawlerProcess(settings=crawler_settings)

    process.crawl(HhRuSpider)
    process.crawl(SuperjobRuSpider)

    process.start()
