import requests
import os
import sys
import time
from terminaltables import AsciiTable
from dotenv import load_dotenv


def get_vacancies_hh(lang):
    moscow_area_number = 1
    page = 0
    pages_number = 1
    pages = []
    while page < pages_number:
        payloads = {
            'text': f'программист {lang}',
            'area': moscow_area_number,
            'page': page
        }
        response = requests.get('https://api.hh.ru/vacancies', params=payloads)
        response.raise_for_status()
        page_payload = response.json()
        pages_number = page_payload['pages']
        pages.append(page_payload)
        page += 1
    return pages


def count_avg_salary(wage_from, wage_to, currency):
    if not wage_from and not wage_to:
        avg_salary = 0
    elif not wage_from or not wage_from and currency == 'RUR' or currency == 'rub':
        avg_salary = wage_to * 0.8
    elif not wage_to or not wage_to and currency == 'RUR' or currency == 'rub':
        avg_salary = wage_from * 1.2
    elif wage_from and wage_to and currency == 'rub' or currency == 'RUR':
        avg_salary = (wage_from + wage_to)/ 2
    elif currency != 'RUR' or currency != 'rub':
        avg_salary = 0    
    return avg_salary
    

def predict_rub_salary_hh(vacancies):
    avg_salary = []
    for page in vacancies:
        for job_adv in page['items']:
            if job_adv['salary']:
                avg_salary.append(count_avg_salary(job_adv['salary']['from'], job_adv['salary']['to'], job_adv['salary']['currency']))
    return avg_salary


def get_hh_statistics(lang, wages, vacancies):
    jobs_counted = len(wages)
    if wages:
        summ = sum(wages)       
    if not jobs_counted:
        avg_salary = 0
    else:
        avg_salary = summ/jobs_counted
    statistics = [lang,
                  vacancies[0]['found'],
                  jobs_counted,
                  avg_salary]
    return statistics


def get_superjob_vacancies(lang, api_id):
    moscow_area_number = 4
    page = 0
    pages_number = 1
    vacancies_per_page = 5
    pages = []
    while page < pages_number:
        headers = {
            'X-Api-App-Id': api_id,
            'page': f'{page}',
            'count': f'{vacancies_per_page}'
            }
        payloads = {
            'keyword':f'программист {lang}',
            'town': f'{moscow_area_number}',
            }
        response = requests.get('https://api.superjob.ru/2.0/vacancies', headers=headers, params=payloads)
        response.raise_for_status()
        page_payload = response.json()
        pages_number = page_payload['total']/vacancies_per_page
        pages.append(page_payload)
        page += 1   
    return pages
    

def predict_rub_salary_for_superJob(vacancies):
    salaries=[]
    for page in vacancies:
        for vacancy in page['objects']:
            avg_salary = count_avg_salary(vacancy['payment_from'], vacancy['payment_to'], vacancy['currency'])
            if avg_salary:
                salaries.append(avg_salary)
    return salaries


def get_sj_statistics(lang, wages, vacancies):
    jobs_counted = len(wages)
    if wages:
        summ = sum(wages)       
    if not jobs_counted:
        avg_salary = 0
    else:
        avg_salary = summ/jobs_counted
    statistics = [lang,
                  vacancies[0]['total'],
                  jobs_counted,
                  avg_salary]
    return statistics


def get_table_sj(languages, api_id):
    table_sj = [
        ['Язык программирования ', 'Вакансий найдено ', 'Вакансий обработано', 'Cредняя зарплата'],
    ]
    for lang in languages:
        vacancies = get_superjob_vacancies(lang, api_id)
        table_sj.append(get_sj_statistics(lang, predict_rub_salary_for_superJob(vacancies), vacancies))
    return table_sj


def print_table_sj(languages, api_id):
    title_sj = 'SuperJob Moscow'
    table_sj = AsciiTable(get_table_sj(languages, api_id), title_sj)
    return print(table_sj.table)


def get_table_hh(languages):
    table_hh = [
        ['Язык программирования ', 'Вакансий найдено ', 'Вакансий обработано', 'Cредняя зарплата'],
    ]
    for lang in languages:
        vacancies = get_vacancies_hh(lang)
        table_hh.append(get_hh_statistics(lang, predict_rub_salary_hh(vacancies), vacancies))
    return table_hh


def print_table_hh(languages):    
    title_hh = 'HeadHunter Moscow'
    table_hh = AsciiTable(get_table_hh(languages), title_hh)
    return print(table_hh.table)


def main():
    load_dotenv()
    api_id = os.environ['SUPERJOB_SECRET_KEY']
    languages = ['Python', 'Java', 'C#', 'C++', 'Ruby']
    try:
        print_table_sj(languages, api_id)
        print_table_hh(languages)
    except requests.HTTPError:
        print('Не возможно найти страницу', file=sys.stderr)
    except requests.exceptions.ConnectionError:
        print('Нет связи с сервером', file=sys.stderr)
        
        

if __name__ == '__main__':
    main()



        

