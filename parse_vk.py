import time

import requests
from lxml import html
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait as wait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from pymongo import MongoClient

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

def get_data(obj):
    data = []
    xpath_string_main = '//div[contains(@class, "post--with-likes")]'
    xpath_string_likes = './/div[contains(@class, "wall-")]//a/div/text()'
    xpath_string_view = './/div[contains(@class, "wall-")]//div[contains(@class,"view")]/text()'
    xpath_string_text = './/div[contains(@class, "wall_post_text")]/text()'
    xpath_string_date = './/div[contains(@class, "post_date")]//span/text()'
    xpath_string_photo = './/a[contains(@aria-label, "фотография")]/@style'
    xpath_string_url = './/a[contains(@class, "post_link")]/@href'

    blocks = obj.xpath(xpath_string_main)

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
        data.append(row)
    print(f'Сollection data from {url} is over')
    return data

driver = webdriver.Chrome(options=options, executable_path=DRIVER_PATH)
driver.get(url)

# Поиск по постам
# post_search(driver, "Джиу")
# time.sleep(3)

time.sleep(1.5)  
scroll_pause = 1 
screen_height = driver.execute_script("return window.screen.height;") 
i = 1

# крутим скролл и ждем всплывающего окна
while True:
    driver.execute_script(f'window.scrollTo(0, {screen_height}*{i});')  
    i += 1
    time.sleep(scroll_pause)
    scroll_height = driver.execute_script('return document.body.scrollHeight;') 

    #if screen_height * i > scroll_height:
    if i == 3:
        break 
wait(driver, 1).until(EC.element_to_be_clickable((By.CLASS_NAME, "JoinForm__notNow"))).click()

# крутим скролл дальше
while True:
    driver.execute_script(f'window.scrollTo(0, {screen_height}*{i});')  
    i += 1
    time.sleep(scroll_pause)
    scroll_height = driver.execute_script('return document.body.scrollHeight;') 
    # можно крутить скролл до конца
    #if screen_height * i > scroll_height:
    if i == 50:
        break 

parse_data = get_data(html.fromstring(driver.page_source))

with MongoClient(MONGO_URL) as client:
    db = client[MONGO_DB]
    collection = db['posts']
    collection.insert_many(parse_data)
    print('Data added into the database')
    
driver.quit()

