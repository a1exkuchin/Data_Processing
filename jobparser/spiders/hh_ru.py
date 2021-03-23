# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import HtmlResponse
from jobparser.items import JobparserItem

class HhRuSpider(scrapy.Spider):
    name = 'hh_ru'
    allowed_domains = ['hh.ru']
    start_urls = ['https://hh.ru/search/vacancy?area=&fromSearchLine=true&st=searchVacancy&text=python']

    def parse(self, response: HtmlResponse):

        vacancy_items  = response.xpath('//div[contains(@class, "vacancy-serp-item")] \
                            //a[contains(@data-qa, "title")]/@href').getall()

        for vacancy_link in vacancy_items:
            yield response.follow(vacancy_link, callback=self.vacancy_parse)
        
        next_page = response.xpath('//a[contains(@data-qa, "pager-next")]/@href').get()

        print(next_page[8:])
        if next_page:
	        yield response.follow(next_page[8:], callback=self.parse)
        
        pass

    def vacancy_parse(self, response: HtmlResponse):
        name = response.xpath('//h1//text()').get()

        salary = response.xpath('//p[contains(@class, "vacancy-salary")]//span/text()').getall()

        vacancy_link = response.url
        site_scraping = self.allowed_domains[0]
        print(salary, vacancy_link)
        yield JobparserItem(name=name, salary=salary, vacancy_link=vacancy_link, site_scraping=site_scraping)
