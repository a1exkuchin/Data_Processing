# ѕосмотреть документацию к API GitHub, разобратьс€ как вывести список репозиториев дл€ конкретного пользовател€, 
# сохранить JSON-вывод в файле *.json

# –ешение задачи из Linux консоли. 
#  онсольный вариант вывода всех репозитариев пользовател€:
# curl -s https://api.github.com/users/a1exkuchin/repos | jq '.[]|.html_url' 

import requests
import json

url = 'https://api.github.com'
user = 'a1exkuchin'

r = requests.get(f'{url}/users/{user}/repos')

# ¬ыводим список репозитариев
for repo in r.json():
    print(repo['html_url'])

# —охран€ем JSON-вывод в файле
with open('data.json', 'w') as f:
    json.dump(r.json(), f)