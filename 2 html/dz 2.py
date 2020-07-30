import requests
from bs4 import BeautifulSoup as bs
import re
import pandas as pd

search = input('Поиск вакансии: ')

header = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36'}

# тянем с SuperJob
superjob_link = 'https://www.superjob.ru'
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

vacancies = pd.DataFrame(vacs)

while True:
    params = {
        'keywords': search,
        'noGeo': '1',
        'page': page
    }
    sj_html = requests.get(superjob_link + '/vacancy/search/', params=params)
    soup = bs(sj_html.text, 'lxml')

    vac_list = soup.findAll('div', {'class': 'f-test-vacancy-item'})
    for vac in vac_list:
        vacancy_data = {}
        min_salary = None
        max_salary = None
        currency = None
        vac_name = vac.find('a', {'class': '_6AfZ9'}).getText()
        vac_link = vac.find('a', {'class': '_6AfZ9'})['href']

        if vac.find('a', {'class': '_25-u7'}) != None:
            employer = vac.find('a', {'class': '_25-u7'}).getText()
        else:
            employer = None

        if vac.find('span', {'class': 'f-test-text-company-item-location'}).findChildren()[-1].getText() != None:
            location = vac.find('span', {'class': 'f-test-text-company-item-location'}).findChildren()[-1].getText()
        else:
            location = None

        source = 'superjob.ru'

        raw_salary = vac.find('span', {'class': '_2VHxz'}).getText()
        if re.findall(r'\S\w+', raw_salary)[-1] != 'договорённости':
            if 'до' in raw_salary:
                max_salary = ''.join(re.findall(r'\d', raw_salary))
                currency = re.findall(r'\S\w+', raw_salary)[-1]
            elif 'от' in raw_salary:
                min_salary = ''.join(re.findall(r'\d', raw_salary))
                currency = re.findall(r'\S\w+', raw_salary)[-1]
            elif '—' in raw_salary:
                salary_range = re.split(r'—', ''.join(re.findall(r'\d|—', raw_salary)))
                min_salary = salary_range[0]
                max_salary = salary_range[1]
                currency = re.findall(r'\S\w+', raw_salary)[-1]

        vacancy_data = pd.DataFrame({'name': [vac_name],
                                     'link': [vac_link],
                                     'location': [location],
                                     'employer': [employer],
                                     'source': [source],
                                     'min_salary': [min_salary],
                                     'max_salary': [max_salary],
                                     'currency': [currency]
                                     })

        vacancies = pd.concat([vacancies, vacancy_data], axis=0)

    if soup.find('div', {'class': '_GJem'}) == None:
        break
    else:
        page_check = soup.find('div', {'class': '_GJem'}).getText()
        if 'Дальше' in page_check:
            page += 1
        else:
            break

new_file = 'result.csv'
vacancies.to_csv(new_file, index=False, encoding='utf-8')

"""
page = 0
main_link = 'https://hh.ru'
params = {
    'L_is_autosearch':'false',
    'clusters':'true',
    'enable_snippets':'true',
    'text':'Data science',
    'page':'0'
}


html = requests.get('https://www.superjob.ru')
soup = bs(html.text, 'lxml')

vac_block = soup.find('div', {'class':'vacancy-serp'})
vac_list = vac_block.findAll('div', {'class': 'vacancy-serp__vacancy'})

vacs = []

for vac in vac_list:
    vac_data = {}
    vac_name = vac.find('div', {'class': 'vacancy-serp-item__row_header'}).children[-1].getText()
    vac_employer = vac
print(0)
# https://hh.ru/search/vacancy?L_is_autosearch=false&clusters=true&enable_snippets=true&text=Data+science&page=1
bs.g

"""
