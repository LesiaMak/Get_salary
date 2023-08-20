import requests
import os
import sys
import time
from terminaltables import AsciiTable
from dotenv import load_dotenv


def get_vac_hh(lang):
    Moscow_area_number = 1
    page = 0
    pages_number = 1
    pages = []
    while page < pages_number:
        payloads = {
            'text': f'программист {lang}',
            'area': Moscow_area_number,
            'page': page
        }
        response = requests.get('https://api.hh.ru/vacancies', params=payloads)
        response.raise_for_status()
        page_payload = response.json()
        pages_number = page_payload['pages']
        pages.append(page_payload)
        page += 1
    return pages


def get_hh_salary(lang):
    for page in get_vac_hh(lang):
        salary = [item['salary'] for item in page['items']]
    return salary


def count_avg_salary(wage_from, wage_to, currency):
    if wage_from is None and wage_to is None:
        avg_salary = None
    elif not wage_from and not wage_to:
        avg_salary = None
    elif wage_from is None or not wage_from and currency == 'RUR' or currency == 'rub':
        avg_salary = wage_to * 0.8
    elif wage_to is None or not wage_to and currency == 'RUR' or currency == 'rub':
        avg_salary = wage_from * 1.2
    elif wage_from and wage_to and currency == 'rub' or currency == 'RUR':
        avg_salary = (wage_from + wage_to)/ 2
    elif currency != 'RUR' or currency != 'rub':
        avg_salary = None

    
    return avg_salary
    

def predict_rub_salary_hh(lang):
    salary_items = get_hh_salary(lang)
    avg_salary = []
    for item in salary_items:
        if item:
           avg_salary.append(count_avg_salary(item['from'], item['to'], item['currency']))
        else:
            avg_salary.append(None)
    return avg_salary

def get_hh_statistics(lang):
    wages = predict_rub_salary_hh(lang)
    jobs_counted = 0
    summ = 0
    for wage in wages:
        if wage is not None:
            jobs_counted = jobs_counted + 1
            summ = summ + wage       
    if jobs_counted == 0:
        avg_salary = 0
    else:
        avg_salary = summ/jobs_counted
    
    statistics = {lang:{
                    "vacancies_found": get_vac_hh(lang)[0]['found'],
                    "vacancies_processed": jobs_counted,
                    "average_salary": int(avg_salary),
                }}
    return statistics


def get_superjob_vac(lang, api_id):
    Moscow_area_number = 4
    page = 0
    pages_number = 1
    pages = []
    while page < pages_number:
        headers = {
            'X-Api-App-Id': api_id,
            'page': f'{page}',
            }
        payloads = {
            'keyword':f'программист {lang}',
            'town': f'{Moscow_area_number}',
            }
        response = requests.get('https://api.superjob.ru/2.0/vacancies', headers=headers, params=payloads)
        response.raise_for_status()
        page_payload = response.json()
        pages_number = 500
        pages.append(page_payload)
        page += 1   
    return pages

def predict_rub_salary_for_superJob(lang, api_id):
    salaries = []
    for page in get_superjob_vac(lang, api_id):
        for item in page['objects']:
            salaries.append(count_avg_salary(
                item['payment_from'], 
                item['payment_to'], 
                item['currency']
                )
                )

    return salaries

def get_sj_statistics(lang, api_id):
    wages = predict_rub_salary_for_superJob(lang, api_id)
    jobs_counted = 0
    summ = 0
    for wage in wages:
        if wage:
            jobs_counted = jobs_counted + 1
            summ = summ + wage       
    if jobs_counted == 0:
        avg_salary = 0
    else:
        avg_salary = summ/jobs_counted
    statistics = {lang:{
                    "vacancies_found": len(wages),
                    "vacancies_processed": jobs_counted,
                    "average_salary": int(avg_salary),
                }}
    return statistics

def print_table_sj(languages, api_id):
    title_sj = 'SuperJob Moscow'
    table_sj = [
        ['Язык программирования ', 'Вакансий найдено ', 'Вакансий обработано', 'Cредняя зарплата'],
    ]
    for lang in languages:
        stat_sj = get_sj_statistics(lang, api_id)[lang]
        table_sj.append([lang, stat_sj['vacancies_found'], stat_sj['vacancies_processed'], stat_sj['average_salary']])
    table_sj = AsciiTable(table_sj, title_sj)
    return print(table_sj.table)

def print_table_hh(languages):    
    title_hh = 'HeadHunter Moscow'
    table_hh = [
        ['Язык программирования ', 'Вакансий найдено ', 'Вакансий обработано', 'Cредняя зарплата'],
    ]
    for lang in languages:
        stat_hh = get_hh_statistics(lang)[lang]
        table_hh.append([lang, stat_hh['vacancies_found'], stat_hh['vacancies_processed'], stat_hh['average_salary']])
    table_hh = AsciiTable(table_hh, title_hh)
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



        

