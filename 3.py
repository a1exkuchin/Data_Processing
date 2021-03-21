from vscrap import VacancyScrap

vacancies = ['delphi', 'c++', 'python']

url = 'https://www.superjob.ru/clients/efimov-i-partnery-251241.html'

# Проверка существоания вакансии в базе данных 
for job_name in vacancies:
    job_vacancy = VacancyScrap('127.0.0.1:27017', 'job', job_name)
    if job_vacancy.is_exists('vacancy_link', url):
        print('Link found')
        
#Проверка существования вакансии добавлена в функции superjob_parser и hh_parser
#В базу добавляются только те позиции, которых еще не было.