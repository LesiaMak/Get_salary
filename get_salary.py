import requests
import os
import sys
import time
from terminaltables import AsciiTable
from dotenv import load_dotenv


def get_vac_hh(lang):
    page = 0
    pages_number = 1
    pages = []
    while page < pages_number:
        payloads = {
            'text': f'программист {lang}',
            'area': 1,
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
    salary = []
    for page in get_vac_hh(lang):
        for item in page['items']:
            salary.append(item['salary'])
    return salary


def predict_rub_salary_hh(lang):
    salary_items = get_hh_salary(lang)
    avg_salary = []
    for item in salary_items:
        if item:      
            if item['from'] is None and item['currency'] == 'RUR':
                avg_salary.append(item['to'] * 0.8)
            elif item['to'] is None and item['currency'] == 'RUR':
                avg_salary.append(item['from'] * 1.2)
            elif item['currency'] == 'RUR':
                avg_salary.append((item['from'] + item['to'])/ 2)
            elif item['currency'] != 'RUR':
                avg_salary.append(None)
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

    statistics = {lang:{
                    "vacancies_found": get_vac_hh(lang)[0]['found'],
                    "vacancies_processed": jobs_counted,
                    "average_salary": int(summ/jobs_counted),
                }}
    return statistics


def get_superjob_vac(lang, api_id):
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
            'town': '4',
            }
        response = requests.get('https://api.superjob.ru/2.0/vacancies', headers=headers, params=payloads)
        response.raise_for_status()
        page_payload = response.json()
        pages_number = 10
        pages.append(page_payload)
        page += 1   
    return pages

def predict_rub_salary_for_superJob(lang, api_id):
    salaries = []
    for page in get_superjob_vac(lang, api_id):
        for item in page['objects']:
            if item['payment_from'] != 0 and item['payment_to'] != 0 and item['currency'] == 'rub':
                salaries.append((item['payment_from'] + item['payment_to'])/ 2)
            elif item['payment_from'] == 0 and item['payment_to'] == 0:
                salaries.append(None)
            elif item['payment_from'] == 0 and item['currency'] == 'rub':
                salaries.append(item['payment_to'] * 0.8)
            elif item['payment_to'] == 0 and item['currency'] == 'rub':
                salaries.append(item['payment_from'] * 1.2)           
            elif item['currency'] != 'rub':
                salaries.append(None)
    return(salaries)

def get_sj_statistics(lang, api_id):
    wages = predict_rub_salary_for_superJob(lang, api_id)
    jobs_counted = 0
    summ = 0
    for wage in wages:
        if wage is not None:
            jobs_counted = jobs_counted + 1
            summ = summ + wage       

    statistics = {lang:{
                    "vacancies_found": len(wages),
                    "vacancies_processed": jobs_counted,
                    "average_salary": int(summ/jobs_counted),
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
    languages = ['Python', 'Java', 'C#', 'C++']
    try:
        print_table_sj(languages, api_id)
        print_table_hh(languages)
    except requests.HTTPError:
        print('Не возможно найти страницу', file=sys.stderr)
    except requests.exceptions.ConnectionError:
        print('Нет связи с сервером', file=sys.stderr)
        
        

if __name__ == '__main__':
    main()



        

