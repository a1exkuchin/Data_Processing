from vscrap import VacancyScrap
from pprint import pprint

vacancies = ['delphi', 'c++', 'python']

while True:
    try:
        query = int(input('Enter your desired salary (integer): '))
        break
    except:
        print('You entered a non-integer number')
query_result = []
for job_name in vacancies:
    job_vacancy = VacancyScrap('127.0.0.1:27017', 'job', job_name)
    query_result += job_vacancy.search_gt_salary(query)

pprint(query_result)


