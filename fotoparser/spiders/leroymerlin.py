import scrapy
from scrapy.http import HtmlResponse
from scrapy.loader import ItemLoader
from fotoparser.items import FotoparserItem

class LeroymerlinSpider(scrapy.Spider):
    name = 'leroymerlin'
    allowed_domains = ['leroymerlin.ru']

    def __init__(self, search):
        super(LeroymerlinSpider, self).__init__()
        self.start_urls = [f'https://leroymerlin.ru/search/?q={search}']

    def parse(self, response: HtmlResponse):
        links = response.xpath("//product-card/@data-product-url")
        for link in links:
            yield response.follow(link, callback=self.parse_product)

        pass

    def parse_product(self, response: HtmlResponse):
        loader = ItemLoader(item=FotoparserItem(), response=response)
        loader.add_xpath("name", '//h1/text()')
        loader.add_xpath("photos", '//img[contains(@alt, "product image")]/@src')

        yield loader.load_item()

