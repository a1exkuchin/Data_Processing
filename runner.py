from scrapy.settings import Settings
from scrapy.crawler import CrawlerProcess

from fotoparser import settings
from fotoparser.spiders.leroymerlin import LeroymerlinSpider
from urllib.parse import quote_plus


if __name__ == "__main__":
    crawler_settings = Settings()
    crawler_settings.setmodule(settings)
    # search = input("Введите свой запрос: ")
    search = 'доска'
    search = quote_plus(search.encode("utf-8"))
    process = CrawlerProcess(settings=crawler_settings)
    process.crawl(LeroymerlinSpider, search=search)

    process.start()
