from vscrap import VacancyScrap
from pprint import pprint

vacancies = ['delphi', 'c++', 'python']

# Выбор вакансий, у которых отсутсвуют минимальное и максимальное значения 
query_result = []

for job_name in vacancies:
    job_vacancy = VacancyScrap('127.0.0.1:27017', 'job', job_name)
    query_result += job_vacancy.search_empty_salary()

#pprint(query_result)

