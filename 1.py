from vscrap import VacancyScrap

vacancies = ['delphi', 'c++', 'python']
# формируем базу нужных нам вакансий
for job_name in vacancies:
    job_vacancy = VacancyScrap('127.0.0.1:27017', 'job', job_name)
    job_vacancy.search_and_write_job(job_name)
    print(f'Collection {job_name} was created.')