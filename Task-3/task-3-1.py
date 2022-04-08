import re
from bs4 import BeautifulSoup as bs
from pymongo import MongoClient
import requests
from pprint import pprint
# import pymongo
from pymongo.server_api import ServerApi

#https://hh.ru/vacancies/designer?page=1&hhtmFrom=vacancy_search_catalog
# https://hh.ru/search/vacancy?
# clusters=true&
# area=1&
# ored_clusters=true&
# enable_snippets=true&
# salary=&
# text=design&
# page=3

client = MongoClient('127.0.0.1', 27017)
db = client['vacancy_hh']
collection = db.collection
#last_page = 40

url = 'https://hh.ru/vacancy/'
base_url = 'https://hh.ru/search/vacancy?clusters=true&area=1&ored_clusters=true&enable_snippets=true&salary=&&hhtmFrom=vacancy_search_list'
headers = {'user-agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:69.0) Gecko/20100101 Firefox/69.0'}


''' --------------------------------------------------------------------------------------- '''
vacancies_list = []
vacancy_data = {}

for page in range(0, 40):
    params = {'text': 'design',
              'page': page}

    response = requests.get(base_url, params=params, headers=headers)
    dom = bs(response.text, 'html.parser')

    vacancies = dom.find_all('div', {'class': 'vacancy-serp-item-body'})

    for vacancy in vacancies:
        vacancy_data = {} # на каждую итерацию будем содавать словарь с данными
        vacancy_name = vacancy.find('span', {'class': 'g-user-content'}).getText()
        vacancy_link = vacancy.find('a', {'class': 'bloko-link'})['href']
        vacancy_company = vacancy.find('div', {'class': 'vacancy-serp-item__meta-info-company'}).getText().replace(u'\xa0', u' ')
        vacancy_city = vacancy.find('div', {'class': 'bloko-text bloko-text_no-top-indent'}).getText()
        vacancy_salary = vacancy.find('span', {'class': 'bloko-header-section-3'})

        salary_min = None
        salary_max = None
        salary_currency = None

        if vacancy_salary:

            vacancy_salary = vacancy_salary.getText() \
                            .replace(u'\xa0', u'')

            vacancy_salary = re.split(r'\s|-', vacancy_salary)

            if vacancy_salary[0] == 'до':
                if vacancy_salary[2] == '000':
                    salary_max = int(vacancy_salary[1] + vacancy_salary[2])
                else:
                    salary_max = int(vacancy_salary[1])
            elif vacancy_salary[0] == 'от':
                if vacancy_salary[2] == '000':
                    salary_min = int(vacancy_salary[1] + vacancy_salary[2])
                else:
                    salary_min = int(vacancy_salary[1])
            else:
                if vacancy_salary[1]:
                    if vacancy_salary[1] == '000':
                        salary_min = int(vacancy_salary[0]+vacancy_salary[1])
                    else:
                        salary_min = int(vacancy_salary[0])
                else:
                    salary_min = int(vacancy_salary[0])
                if vacancy_salary:
                    if vacancy_salary[4] == '000':
                        salary_max = int(vacancy_salary[3] + vacancy_salary[4])
                    else:
                        salary_max = int(vacancy_salary[3])
                else:
                    salary_max = int(vacancy_salary[3])
            salary_currency = vacancy_salary[-1]

        vacancy_data['name'] = vacancy_name
        vacancy_data['link'] = vacancy_link
        vacancy_data['company'] = vacancy_company
        vacancy_data['city'] = vacancy_city
        vacancy_data['salary_min'] = salary_min
        vacancy_data['salary_max'] = salary_max
        vacancy_data['salary_currency'] = salary_currency
        vacancies_list.append(vacancy_data)

vacancy = vacancies_list

#collection.insert_many(vacancy)

''' --------------------------------------------------------------------------------------- '''
# у каждой вакансии свой урл, по нему и будем искать:

for item in vacancies:
    vacancy = vacancy_data
    if collection.find({'link': vacancy_data['link']}):
        collection.update_one({'link': vacancy_data['link']}, {'$set': vacancy})
    else:
        collection.insert_one(vacancy)

''' --------------------------------------------------------------------------------------- '''

#for item in collection.find({}):
#    pprint(item)

# for item in collection.find({'company': 'DreamCraft'}):
#     pprint(item)
