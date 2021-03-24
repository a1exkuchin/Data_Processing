# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import HtmlResponse
from jobparser.items import JobparserItem

class HhRuSpider(scrapy.Spider):
    name = 'hh_ru'
    allowed_domains = ['hh.ru']
    start_urls = ['https://hh.ru/search/vacancy?area=&fromSearchLine=true&st=searchVacancy&text=python']

    def parse(self, response: HtmlResponse):
        next_page = response.css('a.HH-Pager-Controls-Next::attr(href)').get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)
        vacancy_items = response.xpath('//div[contains(@class, "vacancy-serp-item")] \
                            //a[contains(@data-qa, "title")]/@href').getall()

        for vacancy_link in vacancy_items:
            yield response.follow(vacancy_link, callback=self.vacancy_parse)
            
    def vacancy_parse(self, response: HtmlResponse):
        name = response.xpath('//h1//text()').get()
        salary = response.xpath('//p[contains(@class, "vacancy-salary")]//span/text()').getall()
        vacancy_link = response.url
        site_scraping = self.allowed_domains[0]
        yield JobparserItem(name=name, 
                            salary=salary, 
                            vacancy_link=vacancy_link, 
                            site_scraping=site_scraping)