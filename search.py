from pymongo import MongoClient
from prettytable import PrettyTable

MONGO_URI = "127.0.0.1:27017"
MONGO_DB = "socialnet"


def is_exists(name_tags, field):
    return bool(collection.find_one({name_tags: { "$in": [field]}}))


def table_print(data):
    mytable = PrettyTable()
    mytable.field_names = ["№ п.п.", "ID пользователя", "Имя пользователя"]
    mytable.add_rows(data)
    print(mytable)


def db_find(user, parametr):
    result = []
    subs = [elem for elem in collection.find({'user': user, parametr: True})]
    for i, sub in enumerate(subs):
        result.append([i, sub['user_id'], sub['name']])
    return result        

       
with MongoClient(MONGO_URI) as client:
    db = client[MONGO_DB]
    collection = db['instagram']
    while True:
        user_for_scrape = input('Введите пользователя для поиска подписок и подписчиков: ')
        if is_exists('user', user_for_scrape):
            break
        else:
            print('Пользователь не найден')
    followers = db_find(user_for_scrape, 'follower')
    subscriptions = db_find(user_for_scrape, 'subs')
    print(f'Подписки пользователя {user_for_scrape}')
    table_print(subscriptions)
    print()
    print(f'Подписчики пользователя {user_for_scrape}')
    table_print(followers)


