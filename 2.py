# Изучить список открытых API. Найти среди них любое, требующее авторизацию 
# (любого типа). Выполнить запросы к нему, пройдя авторизацию. 
# Ответ сервера записать в файл.

import requests
import json

url = 'https://api.nasa.gov'
token = 'Pka6S4t3cp6Yfk1d26Z1CSlgszM5Bv1WcSKqgLuo'
mars_photo_path = '/mars-photos/api/v1/rovers/curiosity/photos'
sol = 3000

r = requests.get(f'{url}/planetary/apod?api_key={token}')

# Выводим данные из раздела "Астрономическая картина дня"
for key, value in r.json().items():
    print(f'{key} : {value}')


r = requests.get(f'{url}{mars_photo_path}?sol={sol}&api_key={token}')

# Сохраняем JSON-вывод данных из раздела "Фотографии марсохода" в файл
with open('mars-photos.json', 'w') as f:
    json.dump(r.json(), f)