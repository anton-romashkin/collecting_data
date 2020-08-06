import requests
from bs4 import BeautifulSoup as bs
import re
import pandas as pd
import time


def format_salary(raw_salary):
    """
    Функция для преобразования строки, содержащей зарплатную вилку. Возвращает min_salary, max_salary, currency
    """
    min_salary = None
    max_salary = None
    currency = None
    if 'до' in raw_salary:
        max_salary = ''.join(re.findall(r'\d', raw_salary))
        currency = re.findall(r'\S\w+', raw_salary)[-1]
    elif 'от' in raw_salary:
        min_salary = ''.join(re.findall(r'\d', raw_salary))
        currency = re.findall(r'\S\w+', raw_salary)[-1]
    elif '-' in raw_salary:
        salary_range = re.split(r'-', ''.join(re.findall(r'\d|-', raw_salary)))
        min_salary = salary_range[0]
        max_salary = salary_range[1]
        currency = re.findall(r'\S\w+', raw_salary)[-1]
    return min_salary, max_salary, currency


header = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36'
}

search = input('Поиск вакансии: ')

# создаём пустой dataframe
vacs = {
    "name": [],
    "link": [],
    "location": [],
    "employer": [],
    "source": [],
    "min_salary": [],
    "max_salary": [],
    "currency": [],
}
hh_vacancies = pd.DataFrame(vacs)

# тянем с hh

hh_link = 'https://hh.ru'
hh_addlink = '/search/vacancy'
page = 0

# создаём цикл для смены страниц сайта
while True:
    params = {
        'L_save_area': 'true',
        'clusters': 'true',
        'showClusters': 'true',
        'search_field': 'name',
        'enable_snippets': 'true',
        'text': search,
        'page': page
    }

    hh_html = requests.get(f'{hh_link + hh_addlink}', params, headers=header)
    hh_soup = bs(hh_html.text, 'lxml')

    vac_list = hh_soup.findAll('div', {'class': 'vacancy-serp-item'})
    # цикл для перебора вакансий внутри одной страницы
    for vac in vac_list:
        vac_data = {}
        # name
        vac_name = vac.find('a').getText()
        # link
        vac_link = vac.find('a')['href']  # link
        # employer
        if vac.find('a', {'class': 'bloko-link bloko-link_secondary'}).getText() is not None:
            employer = vac.find('a', {'class': 'bloko-link bloko-link_secondary'}).getText()
        else:
            employer = None
        # location
        if vac.find('span', {'data-qa': 'vacancy-serp__vacancy-address'}).getText() is not None:
            location = vac.find('span', {'data-qa': 'vacancy-serp__vacancy-address'}).getText().split(',')[0]
        else:
            location = None
        # source
        source = 'hh.ru'
        # salary
        raw_salary = []
        if len(vac.find('div', {'class': 'vacancy-serp-item__sidebar'}).findChildren()) > 0:
            raw_salary = vac.find('span', {'data-qa': 'vacancy-serp__vacancy-compensation'}).getText()

        min_salary, max_salary, currency = format_salary(raw_salary)

        # dataframe
        # заполняем таблицу для вакансии
        vacancy_data = pd.DataFrame({
            'name': [vac_name],
            'link': [vac_link],
            'location': [location],
            'employer': [employer],
            'source': [source],
            'min_salary': [min_salary],
            'max_salary': [max_salary],
            'currency': [currency]
        })
        # собираем данные по всем вакансиям в одну таблицу
        hh_vacancies = pd.concat([hh_vacancies, vacancy_data], axis=0)
    # проверка для смены страциц - ищем кнопку 'дальше'
    if hh_soup.find('a', {'class': 'HH-Pager-Controls-Next'}) is None:
        break
    else:
        page_check = hh_soup.find('a', {'class': 'HH-Pager-Controls-Next'}).getText()
        if 'дальше' in page_check:
            page += 1
        else:
            break
    # ждём 1 секунду перед сменой страницы сайта
    time.sleep(1)

# тянем с SuperJob

sj_link = 'https://www.superjob.ru'
sj_addlink = '/vacancy/search/'
page = 1

vacs = {
    "name": [],
    "link": [],
    "location": [],
    "employer": [],
    "source": [],
    "min_salary": [],
    "max_salary": [],
    "currency": [],
}

sj_vacancies = pd.DataFrame(vacs)

while True:
    params = {
        'keywords': search,
        'noGeo': '1',
        'page': page
    }

    sj_html = requests.get(f'{sj_link + sj_addlink}', params=params)
    sj_soup = bs(sj_html.text, 'lxml')

    vac_list = sj_soup.findAll('div', {'class': 'f-test-vacancy-item'})
    for vac in vac_list:
        vac_data = {}
        # name
        vac_name = vac.find('a', {'class': '_6AfZ9'}).getText()
        # link
        vac_link = vac.find('a', {'class': '_6AfZ9'})['href']
        # employer
        if vac.find('a', {'class': '_25-u7'}) is not None:
            employer = vac.find('a', {'class': '_25-u7'}).getText()
        else:
            employer = None
        # location
        if vac.find('span', {'class': 'f-test-text-company-item-location'}).findChildren()[-1].getText() is not None:
            location = vac.find('span', {'class': 'f-test-text-company-item-location'}).findChildren()[2].getText().split(',')[0]
        else:
            location = None
        # source
        source = 'superjob.ru'
        # salary
        raw_salary = []
        if len(vac.find('span', {'class': '_2VHxz'})) > 0 and re.findall(r'\S\w+', vac.find('span', {'class': '_2VHxz'}).getText())[-1] != 'договорённости':
            raw_salary = vac.find('span', {'class': '_2VHxz'}).getText()

        min_salary, max_salary, currency = format_salary(raw_salary)

        # заполняем таблицу для вакансии
        vacancy_data = pd.DataFrame({'name': [vac_name],
                                     'link': [vac_link],
                                     'location': [location],
                                     'employer': [employer],
                                     'source': [source],
                                     'min_salary': [min_salary],
                                     'max_salary': [max_salary],
                                     'currency': [currency]
                                     })
        # объединяем данные в одну таблицу
        sj_vacancies = pd.concat([sj_vacancies, vacancy_data], axis=0)
    # проверка страниц, ищем кнопку 'Дальше'
    if sj_soup.find('div', {'class': '_GJem'}) is None:
        break
    else:
        page_check = sj_soup.find('div', {'class': '_GJem'}).getText()
        if 'Дальше' in page_check:
            page += 1
        else:
            break
    # ждём секунду перед сменой страницы
    time.sleep(1)

# объединяем данные с разных сайтов
vacancies = pd.concat([hh_vacancies, sj_vacancies], axis=0)

new_file = 'result.csv'
vacancies.to_csv(new_file, index=False, encoding='utf-8')

