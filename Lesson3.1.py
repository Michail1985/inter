from pymongo import MongoClient
import json  # подключили библиотеку для работы с json
from pprint import pprint  # подключили Pprint для красоты выдачи текста

with open('Vacancy.json', 'r') as f:  # открыли файл с данными из второго задания(сохранял в json)
    text = json.load(f)  # загнали все, что получилось в переменную

MONGO_URI = "127.0.0.1:27017"
MONGO_DB = "Vacancy"

with MongoClient(MONGO_URI) as client:
    db = client[MONGO_DB]
    Vacancy_db = db.vacancy_new

    Vacancy_db.insert_many(text)
    pprint(Vacancy_db)