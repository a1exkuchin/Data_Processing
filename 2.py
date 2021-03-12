# Изучить список открытых API. Найти среди них любое, требующее авторизацию 
# (любого типа). Выполнить запросы к нему, пройдя авторизацию. 
# Ответ сервера записать в файл.
import requests
import json
import os
from dotenv import load_dotenv
from pprint import pprint

load_dotenv()
token = os.getenv("token")

url = 'https://api.nasa.gov'
mars_photo_path = '/mars-photos/api/v1/rovers/curiosity/photos'
param = {'sol':3000, 'api_key':token}

r = requests.get(url+mars_photo_path, params = param)

# Выводим данные из раздела "Фотографии марсохода" 
pprint(r.text)

# Сохраняем JSON-вывод данных из раздела "Фотографии марсохода" в файл
with open('mars-photos.json', 'w') as f:
    json.dump(r.json(), f, indent=2)