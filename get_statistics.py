

def get_statistics(lang, wages, total_vacancies):
    jobs_counted = len(wages)
    summ = sum(wages)       
    if not jobs_counted:
        avg_salary = 0
    else:
        avg_salary = summ/jobs_counted
    statistics = [lang,
                  total_vacancies,
                  jobs_counted,
                  avg_salary]
    return statistics