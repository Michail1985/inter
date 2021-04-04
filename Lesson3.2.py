# Задание 2
from pymongo import MongoClient
MONGO_URI = "127.0.0.1:27017"
MONGO_DB = "Vacancy"

with MongoClient(MONGO_URI) as client:
    db = client[MONGO_DB]
    Vacancy_db = db.vacancy_new
    for m in Vacancy_db.find({"salary_min": { '$gte': 600000 }}):
        print(m)