import re
import pickle
import requests
from bs4 import BeautifulSoup as bs
import pandas as pd

headers = {
    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 \
    (KHTML, like Gecko) Chrome/88.0.4324.190 Safari/537.36"
}

#proxies = {
#    'http': 'http://3.88.169.225:80',
#    'https': 'https://95.141.193.14:80'
#}

proxies ={}

def save_pickle(o, path):
    with open(path, 'wb') as f:
        pickle.dump(o, f)

def load_pickle(path):
    with open(path, 'rb') as f:
        return pickle.load(f)

def get(url, headers, params, proxies):
    r = requests.get(url, headers=headers, params=params, proxies=proxies)
    return r


def hh_item(item):
    data = {}

    # vacancy_name
    vacancy_name = item.find('span', {'class': 'resume-search-item__name'}) \
        .getText() \
        .replace(u'\xa0', u' ')

    data['vacancy_name'] = vacancy_name

    # company_name
    company_name = item.find('div', {'class': 'vacancy-serp-item__meta-info'}) \
        .find('a') \
        .getText()

    data['company_name'] = company_name.strip()

    # city
    city = item.find('span', {'class': 'vacancy-serp-item__meta-info'}) \
        .getText() \
        .split(', ')[0]

    data['city'] = city.strip()

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
            salary_max = int(salary[1])

        salary_currency = salary[2]

    data['salary_min'] = salary_min
    data['salary_max'] = salary_max
    data['salary_currency'] = salary_currency

    # link
    vacancy_link = item.find('span', {'class': 'resume-search-item__name'}) \
        .find('a')['href']

    data['vacancy_link'] = vacancy_link

    # site
    data['site'] = 'https://hh.ru'

    return data


def hh_parser(vacancy):
    data = []

    params = {
        'text': vacancy,
        'search_field': 'name',
        'items_on_page': '100',
        'page': ''
    }

    url = 'https://hh.ru/search/vacancy'

    html = get(url, headers, params, proxies)
    # надо вставить try except (если не ок то не определено end_page)
    if html.ok:
        parsed_html = bs(html.text, 'html.parser')

        page_block = parsed_html.find('div', {'data-qa': 'pager-block'})
        if not page_block:
            end_page = 1
        else:
            end_page = int(page_block.find_all('a', \
            {'class': 'HH-Pager-Control'})[-2].getText())

    for page in range(end_page):
        params['page'] = page
        html = get(url, headers, params, proxies)
        # надо вставить try except
        if html.ok:
            parsed_html = bs(html.text, 'html.parser')

            vacancy_items = parsed_html.find('div', {'data-qa': 'vacancy-serp__results'}) \
                .find_all('div', {'class': 'vacancy-serp-item'})

            for item in vacancy_items:
                data.append(hh_item(item))

    return data


def superjob_item(item):
    data = {}

    # vacancy_name
    vacancy_name = item.find_all('a')
    if len(vacancy_name) > 1:
        vacancy_name = vacancy_name[-2].getText()
    else:
        vacancy_name = vacancy_name[0].getText()
    data['vacancy_name'] = vacancy_name

    # company_name
    company_name = item.find('span', {'class': 'f-test-text-vacancy-item-company-name'})

    if not company_name:
        company_name = item.findParent() \
            .find('span', {'class': 'f-test-text-vacancy-item-company-name'}) \
            .getText()
    else:
        company_name = company_name.getText()

    data['company_name'] = company_name.strip()

    # city
    company_location = item.find('span', {'class': '_3mfro f-test-text-company-item-location _9fXTd _2JVkc _2VHxz'}) \
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


def superjob_parser(vacancy):
    data = []

    params = {
        'keywords': vacancy,
        'profession_only': '1',
        'geo[c][0]': '15',
        'geo[c][1]': '1',
        'geo[c][2]': '9',
        'page': ''
    }

    link = 'https://www.superjob.ru/vacancy/search/'

    html = requests.get(link, params=params, headers=headers)
    # надо вставить try except (если не ок то не определено end_page)
    if html.ok:
        parsed_html = bs(html.text, 'html.parser')

        page_block = parsed_html.find('a', {'class': 'f-test-button-1'})
    if not page_block:
        end_page = 1
    else:
        page_block = page_block.findParent()
        end_page = int(page_block.find_all('a')[-2].getText())

    for page in range(1, end_page + 1):
        params['page'] = page
        html = requests.get(link, params=params, headers=headers)

        if html.ok:
            parsed_html = bs(html.text, 'html.parser')
            vacancy_items = parsed_html.find_all('div', {'class': 'f-test-vacancy-item'})

            for item in vacancy_items:
                data.append(superjob_item(item))

    return data

vacancy = input('What vacancy you want search? ')
data = []
data.extend(hh_parser(vacancy))
data.extend(superjob_parser(vacancy))
df = pd.DataFrame(data)
save_pickle(df, vacancy+'.pkl')
