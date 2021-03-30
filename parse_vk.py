# import os
import time

import requests
from lxml import html
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from pymongo import MongoClient
from selenium.common import exceptions


DRIVER_PATH = "./chromedriver"
MONGO_URL = 'mongodb://127.0.0.1:27017/'
MONGO_DB = 'tokyofashion'
url = "https://vk.com/tokyofashion"

options = Options()
options.add_argument("--start-maximized")


def post_search(odject, string):
    search_input = odject.find_element_by_xpath('//a[contains(@class, "search")]')
    search_input.click()
    search_input = odject.find_element_by_id("wall_search")
    search_input.send_keys(string)
    search_input.send_keys(Keys.ENTER)


def get_parsing_data(url): 
    headers = {'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 \
            (KHTML, like Gecko) Chrome/88.0.4324.190 Safari/537.36"
    }
    r = requests.get(url, headers = headers)
    obj = html.fromstring(r.text)
    return obj


def get_value(elems):
    if len(elems) > 0:
        return str(elems[0])
    return None


def get_all_photo(elems):
    result = []
    for elem in elems:
        elem = str(elem)[:-2].split('(')[-1]
        result.append(elem)
    return result

def get_likes(elems):
    result = []
    for elem in elems:
        result.append(str(elem))
    if len(result) == 1:
        result.append('0')
    return result

def get_data(url):

    data = []
    xpath_string_main = '//div[contains(@class, "post--with-likes")]'
    xpath_string_likes = './/div[contains(@class, "wall-")]//a/div/text()'
    xpath_string_view = './/div[contains(@class, "wall-")]//div[contains(@class,"view")]/text()'
    xpath_string_text = './/div[contains(@class, "wall_post_text")]/text()'
    xpath_string_date = './/div[contains(@class, "post_date")]//span/text()'
    xpath_string_photo = './/a[contains(@aria-label, "фотография")]/@style'
    xpath_string_url = './/a[contains(@class, "post_link")]/@href'

    blocks = get_parsing_data(url).xpath(xpath_string_main)

    for block in blocks:
        row = {}
 
        item = block.xpath(xpath_string_date)
        row['date'] = get_value(item)
    
        item = block.xpath(xpath_string_url)
        row['url'] = 'https://vk.com' + get_value(item)
    
        item = block.xpath(xpath_string_text)
        row['text'] = ' '.join(item).replace('Insta', '').replace('Twitter', '')
    
        item = block.xpath(xpath_string_photo)
        row['photo'] = get_all_photo(item)   
        
        item = block.xpath(xpath_string_likes)
        row['likes'] = get_likes(item)
        item = block.xpath(xpath_string_view)
        row['likes'].append(get_value(item))
        #row['likes'] = zip(['like', 'share', 'view'], row['likes'])
        #row[]

        data.append(row)
    print(f'Сollection data from {url} is over')
    return data

#driver = webdriver.Chrome(options=options, executable_path=DRIVER_PATH)
#driver.get(url)

#post_search(driver, "Джиу")
#time.sleep(3)

 
   
#while True:
#    try:
        # collection.insert_one()
#        pass
#    except exceptions.TimeoutException:
#        print('are over')
#        break

#driver.quit()

parse_data = get_data(url)

with MongoClient(MONGO_URL) as client:
    db = client[MONGO_DB]
    collection = db['posts']
    collection.insert_many(parse_data)
    print('Data added into the database')
    

