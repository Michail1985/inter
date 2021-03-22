from pymongo import MongoClient
import json
import pandas as pd
import re
import pickle
import requests
from bs4 import BeautifulSoup as bs
vacancy = 'Python'
vacancy_date = []

def save_pickle(o, path):
    with open(path, 'wb') as f:
        pickle.dump(o, f)


def load_pickle(path):
    with open(path, 'rb') as f:
        return pickle.load(f)


def get(url, headers, params, proxies):
    html = requests.get(url, headers=headers, params=params, proxies=proxies)
    return html



url = "https://hh.ru/search/vacancy/"
params = {
    'clusters': 'true',
    'enable_snippets': 'true',
    'text': vacancy,
}

headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:69.0) Gecko/20100101 Firefox/69.0'
}

proxies = {
    'http': 'http://3.88.169.225:80',
}
html = get(url, headers, params, proxies)

if html.ok:
    parsed_html = bs(html.text, 'html.parser')

    page_block = parsed_html.find('div', {'data-qa': 'pager-block'})
    if not page_block:
        last_page = '1'
    else:
        last_page = int(page_block.find_all('a', {'class': 'HH-Pager-Control'})[-2].getText())

for page in range(0, last_page):
    params['page'] = page
    html = requests.get(url, params=params, headers=headers)

    if html.ok:
        parsed_html = bs(html.text, 'html.parser')

        vacancy_items = parsed_html.find('div', {'data-qa': 'vacancy-serp__results'}) \
            .find_all('div', {'class': 'vacancy-serp-item'})

        for item in vacancy_items:
            info = {}

            # название вакансии
            vacancy_name = item.find(attrs={"class": "bloko-link"}).text
            vacancy_name = vacancy_name.replace(u'\xa0', u' ')
            vacancy_name = vacancy_name.replace(u'\u200e', u'')
            vacancy_name = vacancy_name.replace(u'\u200b', u'')
            info['vacancy_name'] = vacancy_name

            # минимальное и максимальное значение зарплаты

            salary = item.find(attrs={'class': 'vacancy-serp-item__sidebar'}).text
            if not salary:
                salary_min = None
                salary_max = None
                salary_currency = None
            else:
                salary = salary.replace(u'\xa0', u'')
                #salary = salary.replace(u' - ', '-')
                salary = salary.replace(u'–', u'-')
                salary = re.split(r'\s|-', salary)
                if salary[0] == 'до':
                    salary_min = None
                    salary_max = int(salary[1])
                elif salary[0] == 'от':
                    salary_min = int(salary[1])
                    salary_max = None
                else:
                    salary_min = int(salary[0])
                    salary_max = int(salary[1])
                salary_currency = salary[2]

            info['salary_min'] = salary_min
            info['salary_max'] = salary_max
            info['salary_currency'] = salary_currency

            # ссылка на вакансию
            vacancy_link = item.find(attrs={'class': "g-user-content"}).find('a')['href']
            info['vacancy_link'] = vacancy_link

            # сайт
            info['site'] = 'https://www.hh.ru'
            vacancy_date.append(info)

url = "https://www.superjob.ru/vacancy/search/"
params = {
    'keywords': vacancy,
    'showClusters': 'true',
    'noGeo': 1
}

html = get(url, headers, params, proxies)

if html.ok:
    parsed_html = bs(html.text, 'html.parser')

    page_block = parsed_html.find('a', {'class': 'f-test-button-1'})
if not page_block:
    last_page = 1
else:
    page_block = page_block.findParent()
    last_page = int(page_block.find_all('a')[-2].getText())

for page in range(0, last_page + 1):
    params['page'] = page
    html = requests.get(url, params=params, headers=headers)

    if html.ok:
        parsed_html = bs(html.text, 'html.parser')
        vacancy_items = parsed_html.find_all('div', {'jNMYr'})

        for item in vacancy_items:
            info = {}
            vacancy_name = item.find_all('a', {'class': 'icMQ_'})

            # Название вакансии
            if len(vacancy_name) < 1:
                vacancy_name = None
            else:
                vacancy_name = vacancy_name[-1].getText()
                info['vacancy_name'] = vacancy_name

            # salary
            salary = item.find('span', {'class': '_3mfro'}).text

            if not salary:
                salary_min = None
                salary_max = None
                salary_currency = None
            else:
                #salary = salary.replace(u'\xa0', u'')
                salary = re.split(r'\s|-', salary)

                if salary[0] == 'до':
                    salary_min = None
                    salary_max = int(salary[1]+salary[2])
                    salary_currency = salary[3]
                elif salary[0] == 'от':
                    salary_min = int(salary[1]+salary[2])
                    salary_max = None
                    salary_currency = salary[3]
                elif salary[0] == 'По':
                    salary_min = None
                    salary_max = None
                elif salary[2] == '—':
                    salary_min = int(salary[0] + salary[1])
                    salary_max = int(salary[3] + salary[4])
                    salary_currency = salary[5]
                else:
                    salary_min = int(salary[0] + salary[1])
                    salary_max = int(salary[0] + salary[1])
                    salary_currency = salary[2]

            info['salary_min'] = salary_min
            info['salary_max'] = salary_max
            info['salary_currency'] = salary_currency

            # Ссылка на вакансию
            vacancy_link = item.find_all('a', {'class': 'icMQ_'})

            if len(vacancy_link) < 1:
                vacancy_link = None
            else:
                vacancy_link = vacancy_link[0]['href']
                info['vacancy_link'] = f'https://www.superjob.ru{vacancy_link}'

            # Сайт
            info['site'] = 'https://www.superjob.ru'
            vacancy_date.append(info)

df = pd.DataFrame(vacancy_date)
with open("Vacancy.json", "w") as f:
    json.dump(vacancy_date, f, indent=1, ensure_ascii=False)
print(df)

MONGO_URI = "127.0.0.1:27017"
MONGO_DB = "Vacancy"

with MongoClient(MONGO_URI) as client:
    db = client[MONGO_DB]
    Vacancy_db = db.vacancy_new
    for mv in vacancy_date:
        a = 0
        for m in Vacancy_db.find({"vacancy_link": {'$ne': ''}}):
            if mv['vacancy_link'] == m['vacancy_link']:
                a = 0
                break
            #print(Vacancy_db("vacancy_link"))
            #    print(m['vacancy_link'])
            #    print(mv['vacancy_link'])
            else:
                a = 1
        if a == 1:
            Vacancy_db.insert_one(mv)
            print(mv['vacancy_link'])