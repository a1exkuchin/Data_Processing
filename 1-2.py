import requests
from pymongo import MongoClient
from datetime import datetime, timedelta
from lxml import html

def get_lenta_links(elems):
    links = []
    for elem in elems:
        if str(elem)[:5] == '/news':
            links.append('https://lenta.ru'+str(elem))
    return links

def get_value(elems):
    if len(elems) > 0:
        return elems[0]
    return None

def get_parsing_data(_url): 
    headers = {'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 \
            (KHTML, like Gecko) Chrome/88.0.4324.190 Safari/537.36"
    }
    r = requests.get(_url, headers = headers)
    obj = html.fromstring(r.text)
    return obj

def get_dates_and_news(_urls, _xpath1, _xpath2):        
    date = []
    news = []
    for url in _urls:
        tree = get_parsing_data(url)
        item1 = tree.xpath(_xpath1)
        item2 = tree.xpath(_xpath2)
        date.append(datetime.strptime(str(get_value(item1)), '%Y-%m-%dT%H:%M:%S%z'))
        news.append(str(get_value(item2)))
    return date, news

url_mail = 'https://news.mail.ru'
url_lenta = 'https://lenta.ru'
url_yandex = 'https://news.yandex.ru/news'


def get_news_lenta(_url):

    xpath_string_urls = '//div[contains(@class, "b-tabloid__topic_news")]//a/@href'
    xpath_string_text = '//div[contains(@class, "b-topic_news")]//h1/text()'
    xpath_string_date = '//div[contains(@class, "b-topic__info")]//time/@datetime'

    urls = get_lenta_links(get_parsing_data(_url).xpath(xpath_string_urls))
    dates, news_header = get_dates_and_news(urls, xpath_string_date, xpath_string_text)

    news = []
    keys = ('title', 'date', 'url')       
    for item in list(zip(news_header, dates, urls)):
        news_dict = {}
        for key, value in zip(keys, item):
            news_dict[key] = value
        news_dict['source'] = _url
        news.append(news_dict)
    print('Сollection of news from https://lenta.ru is over')
    return news
       

def get_news_mail(_url):
    
    news = []

    xpath_string_main = '//div[contains(@class, "daynews__item")]//a/@href | //li//a/@href | //div[contains(@class, "newsitem")]//a/@href'
    xpath_string_date = '//span[contains(@class, "note__text")]/@datetime'
    xpath_string_source = '//span[contains(@class, "note")]/a/@href'
    xpath_string_title = '//div[contains(@class, "js-article")]//h1/text()'

    elems = get_parsing_data(_url).xpath(xpath_string_main)

    urls = []
    for elem in elems:
        urls.append(str(elem))
    
    news = [] 
    for url in urls:
        new = {}
        tree = get_parsing_data(url)
    
        item = tree.xpath(xpath_string_date)
        new['date'] = datetime.strptime(str(get_value(item)), '%Y-%m-%dT%H:%M:%S%z')
    
        item = tree.xpath(xpath_string_source)
        new['source'] = str(get_value(item))
    
        item = tree.xpath(xpath_string_title)
        new['title'] = str(get_value(item))
    
        new['url'] = url
        news.append(new)
    print('Сollection of news from https://news.mail.ru is over')
    return news

def get_news_yandex(_url):

    news = []

    xpath_string_main = '//article[contains(@class, "mg-card")]'
    xpath_string_url = './/a/@href'
    xpath_string_title = './/a[@class="mg-card__link"]//text()'
    xpath_string_date = './/span[contains(@class, "mg-card-source__time")]//text()'
    xpath_string_source = './/a[@class="mg-card__source-link"]//text()'

    blocks = get_parsing_data(_url).xpath(xpath_string_main)

    for block in blocks:
        new = {}
 
        item = block.xpath(xpath_string_date)
        string = str(get_value(item)).split()

        #if string[0] == 'вчера':
        #    d = datetime.today() - timedelta(days=1)
        #    string = str(d).split()[0] + ' ' + string.split()[2]
        #string = str(datetime.today()).split()[0] + ' ' + str(get_value(item))
        #new['date'] = datetime.strptime(string,'%Y-%m-%d %H:%M')
        new['date'] = datetime.today()
    
        item = block.xpath(xpath_string_url)
        new['url'] = str(get_value(item))
    
        item = block.xpath(xpath_string_title)
        new['title'] = str(get_value(item))
    
        item = block.xpath(xpath_string_source)
        new['source'] = str(get_value(item))
        news.append(new)
    print('Сollection of news from https://yandex.ru is over')
    return news
    
lenta = get_news_lenta(url_lenta)
mail = get_news_mail(url_mail)
yandex = get_news_yandex(url_yandex)  
        
MONGO_URI = "127.0.0.1:27017"
MONGO_DB = "news"

with MongoClient(MONGO_URI) as client:
    db = client[MONGO_DB]
    collection = db['publications']
    collection.insert_many(lenta)
    collection.insert_many(mail)
    collection.insert_many(yandex)
    print('Data added into the database')

        
        
 
