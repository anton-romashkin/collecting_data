import requests
from bs4 import BeautifulSoup as bs
import re
import pandas as pd
import pprint

search = 'Data science'

header = {
    'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36'}

# тянем с SuperJob

superjob_link = 'https://www.superjob.ru'
page = 1
params = {
    'keywords':'Управляющий салоном',
    'noGeo':'1',
    'page':page
}

vacancies = []

while True:
    sj_html = requests.get(superjob_link + '/vacancy/search/', params=params)
    soup = bs(sj_html.text, 'lxml')

    vac_list = soup.findAll('div', {'class': 'f-test-vacancy-item'})
    for vac in vac_list:
        vacancy_data = {}
        min_salary = None
        max_salary = None
        vac_name = vac.find('a', {'class': '_6AfZ9'}).getText()
        vac_link = vac.find('a', {'class': '_6AfZ9'})['href']
        employer = vac.find('a', {'class': '_25-u7'}).getText()
        location = vac.find('span', {'class': 'f-test-text-company-item-location'}).findChildren()[-1].getText()
        source = 'superjob.ru'
        raw_salary = vac.find('span', {'class': '_2VHxz'}).getText()
        if 'до' in raw_salary:
            max_salary = ''.join(re.findall(r'\d', raw_salary))
        elif 'от' in raw_salary:
            min_salary = ''.join(re.findall(r'\d', raw_salary))
        elif '—' in raw_salary:
            salary_range = re.split(r'—', ''.join(re.findall(r'\d|—', raw_salary)))
            min_salary = salary_range[0]
            max_salary = salary_range[1]

        vacancy_data['name'] = vac_name
        vacancy_data['link'] = vac_link
        vacancy_data['location'] = location
        vacancy_data['employer'] = employer
        vacancy_data['source'] = source
        vacancy_data['min_salary'] = min_salary
        vacancy_data['max_salary'] = max_salary




    page_check = soup.find('div', {'class': '_GJem'}).getText()
    if 'Дальше' in page_check:
        page += 1
    else:
        break



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
