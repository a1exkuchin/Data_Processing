# ���������� ������������ � API GitHub, ����������� ��� ������� ������ ������������ ��� ����������� ������������, 
# ��������� JSON-����� � ����� *.json

# ������� ������ �� Linux �������. 
# ���������� ������� ������ ���� ������������ ������������:
# curl -s https://api.github.com/users/a1exkuchin/repos | jq '.[]|.html_url' 

import requests
import json

url = 'https://api.github.com'
user = 'a1exkuchin'

r = requests.get(f'{url}/users/{user}/repos')

# ������� ������ ������������
for repo in r.json():
    print(repo['html_url'])

# ��������� JSON-����� � �����
with open('data.json', 'w') as f:
    json.dump(r.json(), f)