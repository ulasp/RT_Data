import re
from bs4 import BeautifulSoup as bs
from pymongo import MongoClient
import requests
from pprint import pprint
# import pymongo
from pymongo.server_api import ServerApi
''' 2. Написать функцию, которая производит поиск и выводит
    на экран вакансии с заработной платой больше введённой суммы
    (необходимо анализировать оба поля зарплаты). 
'''
client = MongoClient('127.0.0.1', 27017)
db = client['vacancy_hh']
collection = db.collection

def more_salary(salary):
    items = collection.find({'salary_max': {'$gt': salary}, 'salary_min': {'$gt': salary}})
    for item in items:
        pprint(item)

more_salary(200000)

