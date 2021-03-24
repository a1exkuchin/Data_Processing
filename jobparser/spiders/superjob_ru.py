import scrapy
from scrapy.http import HtmlResponse
from jobparser.items import JobparserItem

class SuperjobRuSpider(scrapy.Spider):
    name = 'superjob_ru'
    allowed_domains = ['superjob.ru']
    start_urls = ['https://russia.superjob.ru/vacancy/search/?keywords=python']

    def parse(self, response):
        next_page = response.css('a.f-test-link-Dalshe::attr(href)').get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

        vacancy_items  = response.css('div.f-test-vacancy-item \
            a[class*=f-test-link][href^="/vakansii"]::attr(href)').getall()

        for vacancy_link in vacancy_items:
            yield response.follow(vacancy_link, self.vacancy_parse)

    def vacancy_parse(self, response: HtmlResponse):
        name = response.xpath('//h1/text()').getall()
        salary = response.xpath('//span[contains(@class, "_1OuF_ ZON4b")]//text()').getall()

        vacancy_link = response.url

        site_scraping = self.allowed_domains[0]
        yield JobparserItem(
            name=name,
            salary=salary, 
            vacancy_link=vacancy_link, 
            site_scraping=site_scraping
        )
