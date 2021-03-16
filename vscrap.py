from bs4 import BeautifulSoup as bs
from pymongo import MongoClient
import re
import requests

class VacancyScrap():

    def __init__(self, mongodb_url, db_name, collection_name):
        self.headers = {
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 \
            (KHTML, like Gecko) Chrome/88.0.4324.190 Safari/537.36"
        }
        self.url_hh = 'https://hh.ru/search/vacancy'
        self.url_seperjob = 'https://www.superjob.ru/vacancy/search/'
        #self.collection_name = collection_name
        self.mongodb = MongoClient(mongodb_url)
        self.db = self.mongodb[db_name]
        self.collection = self.db[collection_name]

    def search_gt_salary(self, salary):
        objects = self.collection.find({'salary_max': {'$gt': salary}})
        result = []
        for obj in objects:
            result.append(obj)
        return result 
            
    def search_empty_salary(self):
        objects = self.collection.find({'salary_max': None, 'salary_min': None})
        result = []
        for obj in objects:
            result.append(obj)
        return result 
            
    def search_and_write_job(self, vacancy):
        self.hh_parser(vacancy)
        self.superjob_parser(vacancy)

    def _get_parsed_html(self, html):
        if html.ok:
            parsed_html = bs(html.text,'html.parser')
            return parsed_html

    def _get_html(self, url, params=None):
        html = requests.get(url, params=params, headers=self.headers)
        return html

    def is_exists(self, name_tags, field):
        return bool(self.collection.find_one({name_tags: { "$in": [field]}}))

    def _get_end_page_hh(self, html):
        parsed_html = self._get_parsed_html(html)
        # надо вставить try except (если не ок то не определено end_page)
        if parsed_html:
            page_block = parsed_html.find('div', {'data-qa': 'pager-block'})
            if not page_block:
                end_page = 1
            else:
                end_page = int(page_block.find_all('a', {'class': 'HH-Pager-Control'})[-2] \
                                .getText())
        return end_page

    def _get_end_page_superjob(self, html):
        parsed_html = self._get_parsed_html(html)
        if parsed_html:
            page_block = parsed_html.find('a', {'class': 'f-test-button-1'})
            if not page_block:
                end_page = 1
            else:
                page_block = page_block.findParent()
                end_page = int(page_block.find_all('a')[-2].getText())
        return end_page

    def hh_parser(self, vacancy):
        params = {
            'text': vacancy,
            'search_field': 'name',
            'items_on_page': '100',
            'page': ''
            }
        html = self._get_html(self.url_hh, params)
        end_page = self._get_end_page_hh(html)
        for page in range(end_page):
            params['page'] = page
            html = self._get_html(self.url_hh, params)
            if html.ok:
                parsed_html = self._get_parsed_html(html)
                vacancy_items = parsed_html.find('div', {'data-qa': 'vacancy-serp__results'}) \
                               .find_all('div', {'class': 'vacancy-serp-item'})
                for item in vacancy_items:
                    vacancy = self.hh_item(item)
                    try:
                        if not (self.is_exists('vacancy_link', vacancy['vacancy_link'])):
                            self.collection.insert_one(vacancy)
                    except:
                        self.collection.insert_one(vacancy)
           
    def superjob_parser(self, vacancy):
        params = {
            'keywords': vacancy,
            'profession_only': '1',
            'geo[c][0]': '15',
            'geo[c][1]': '1',
            'geo[c][2]': '9',
            'page': ''
            }
        html = self._get_html(self.url_seperjob, params)
        end_page = self._get_end_page_superjob(html)
        for page in range(1, end_page + 1):
            params['page'] = page
            html = self._get_html(self.url_seperjob, params)
            if html.ok:
                parsed_html = self._get_parsed_html(html)
                vacancy_items = parsed_html.find_all('div', {'class': 'f-test-vacancy-item'})
                for item in vacancy_items:
                    vacancy = self.superjob_item(item)                
                    try:
                        if not (self.is_exists('vacancy_link', vacancy['vacancy_link'])):
                            self.collection.insert_one(vacancy)
                    except:
                        self.collection.insert_one(vacancy)

    def hh_item(self, item):
        data = {}
        # vacancy_name
        try:
            vacancy_name = item.find('span', {'class': 'resume-search-item__name'}) \
                .getText() \
                    .replace(u'\xa0', u' ')
            data['vacancy_name'] = vacancy_name
        except AttributeError:
            data['vacancy_name'] = ''
        # company_name
        try:
            company_name = item.find('div', {'class': 'vacancy-serp-item__meta-info'}) \
                .find('a') \
                    .getText()
            data['company_name'] = company_name.strip()
        except AttributeError:
            data['company_name'] = ''
        # city
        try:
            city = item.find('span', {'class': 'vacancy-serp-item__meta-info'}) \
                .getText() \
                .split(', ')[0]
            data['city'] = city.strip()
        except AttributeError:
            data['city'] = ''
        # salary
        salary = item.find('span', {'data-qa': 'vacancy-serp__vacancy-compensation'})
        if not salary:
            salary_min = None
            salary_max = None
            salary_currency = None
        else:
            salary = re.split(r'\s|-', salary.text \
            .replace(u'\xa0', u''))
            if salary[0] == 'до':
                salary_min = None
                salary_max = int(salary[1])
            elif salary[0] == 'от':
                salary_min = int(salary[1])
                salary_max = None
            else:
                salary_min = int(salary[0])
                try: 
                    salary_max = int(salary[1])
                except ValueError:
                    salary_max = int(salary[2])
            salary_currency = salary[2]
        data['salary_min'] = salary_min
        data['salary_max'] = salary_max
        data['salary_currency'] = salary_currency
        # link
        try:
            vacancy_link = item.find('span', {'class': 'resume-search-item__name'}) \
                .find('a')['href']
            data['vacancy_link'] = vacancy_link
        except:
            data['vacancy_link'] = ''
        # site
        data['site'] = 'https://hh.ru'
        return data

    def superjob_item(self, item):
        data = {}
        # vacancy_name
        vacancy_name = item.find_all('a')
        if len(vacancy_name) > 1:
            vacancy_name = vacancy_name[-2].getText()
        else:
            vacancy_name = vacancy_name[0].getText()
        data['vacancy_name'] = vacancy_name
        # company_name
        try:
            company_name = item.find('span', \
                {'class': 'f-test-text-vacancy-item-company-name'}) \
                .find('a').getText()
        except AttributeError:
            company_name = ''
        data['company_name'] = company_name.strip()
        # city
        company_location = item.find('span', {'class': 'f-test-text-company-item-location'}) \
                .findChildren()[2].getText().split(',')
        data['city'] = company_location[0].strip()
        #salary
        salary = item.find('span', {'class': '_3mfro _2Wp8I PlM3e _2JVkc _2VHxz'}).text
        salary=salary.replace(u'\xa0', u'')
        if '—' in salary:
            salary_min = int(re.sub(r'[^0-9]', '', salary.split('—')[0]))
            salary_max = int(re.sub(r'[^0-9]', '', salary.split('—')[1]))
            salary_currency = salary[-4:]
        elif 'от' in salary:
            salary_min = int(re.sub(r'[^0-9]', '', salary[2:]))
            salary_max = None
            salary_currency = salary[-4:]
        elif 'договорённости' in salary:
            salary_min = None
            salary_max = None
            salary_currency = None
        elif 'до' in salary:
            salary_min = None
            salary_max = int(re.sub(r'[^0-9]', '', salary[2:]))
            salary_currency = salary[-4:]
        else:
            salary_min = int(re.sub(r'[^0-9]', '', salary))
            salary_max = int(re.sub(r'[^0-9]', '', salary))
            salary_currency = salary[-4:]

        data['salary_min'] = salary_min
        data['salary_max'] = salary_max
        data['salary_currency'] = salary_currency
        # link
        vacancy_link = item.find_all('a')
        if len(vacancy_link) > 1:
            vacancy_link = vacancy_link[-2]['href']
        else:
            vacancy_link = vacancy_link[0]['href']
        data['vacancy_link'] = f'https://www.superjob.ru{vacancy_link}'
        # site
        data['site'] = 'https://www.superjob.ru'
        return data
