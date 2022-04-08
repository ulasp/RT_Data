import re
from bs4 import BeautifulSoup as bs
import requests
from pprint import pprint

#https://hh.ru/vacancies/designer?page=1&hhtmFrom=vacancy_search_catalog
# https://hh.ru/search/vacancy?
# clusters=true&
# area=1&
# ored_clusters=true&
# enable_snippets=true&
# salary=&
# text=design&
# page=3

field_search = 'design'
last_page = 10
page = 0

params = {'text': field_search,
          'page': page}

url = 'https://hh.ru/vacancy/'
base_url = 'https://hh.ru/search/vacancy?clusters=true&area=1&ored_clusters=true&enable_snippets=true&salary=&'

headers = {'user-agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:69.0) Gecko/20100101 Firefox/69.0'}


for page in range(last_page):
    params['page'] = page

    response = requests.get(base_url, params=params, headers=headers)
    dom = bs(response.text, 'html.parser')
    page = +1

vacancies = dom.find_all('div', {'class': 'vacancy-serp-item-body'})

vacancies_list = []
for vacancy in vacancies:
    vacancy_data = {} # на каждую итерацию будем содавать словарь с данными
    vacancy_name = vacancy.find('span', {'class': 'g-user-content'}).getText()
    vacancy_link = vacancy.find('a', {'class': 'bloko-link'})['href']
    vacancy_company = vacancy.find('div', {'class': 'vacancy-serp-item__meta-info-company'}).getText().replace(u'\xa0', u' ')
    vacancy_city = vacancy.find('div', {'class': 'bloko-text bloko-text_no-top-indent'}).getText()
    vacancy_salary = vacancy.find('span', {'class': 'bloko-header-section-3'})
    # salary
    if vacancy_salary:
        vacancy_salary = vacancy_salary.getText().replace('\xa0', ' ', 3)
        vacancy_salary = re.split(r'\s|-', vacancy_salary)
        if vacancy_salary[0] == 'до':
            vacancy_salary_min = None
            vacancy_salary_max = int(vacancy_salary[1]+vacancy_salary[2])
            vacancy_salary_currency = vacancy_salary[3]
        elif vacancy_salary[0] == 'от':
            vacancy_salary_min = int(vacancy_salary[1]+vacancy_salary[2])
            vacancy_salary_max = None
            vacancy_salary_currency = vacancy_salary[3]
        else:
            vacancy_salary_min = int(vacancy_salary[0] + vacancy_salary[1])
            vacancy_salary_max = int(vacancy_salary[3] + vacancy_salary[4])
            vacancy_salary_currency = vacancy_salary[5]


    else:
        vacancy_salary = None
        vacancy_salary_min = None
        vacancy_salary_max = None
        vacancy_salary_currency = None

    vacancy_data['name'] = vacancy_name
    vacancy_data['link'] = vacancy_link
    vacancy_data['company'] = vacancy_company
    vacancy_data['city'] = vacancy_city
    vacancy_data['salary_min'] = vacancy_salary_min
    vacancy_data['salary_max'] = vacancy_salary_max
    vacancy_data['salary_currency'] = vacancy_salary_currency
#    vacancy_data['salary'] = vacancy_salary
#    vacancy_data['cur'] = vacancy_salary_currency

    vacancies_list.append(vacancy_data)

df = pd.DataFrame(vacancies_list)
#print(df)
df.to_csv('file.csv')