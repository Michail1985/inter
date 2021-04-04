from lxml import html
import requests
import pandas as pd
from datetime import datetime, timedelta
from pymongo import MongoClient
from pprint import pprint

news = []
date_format = '%Y-%m-%d'
keys = ('title', 'date', 'link', 'sourse')

# lenta.ru

link_lenta = 'https://lenta.ru/'

request = requests.get(link_lenta)

root = html.fromstring(request.text)
root.make_links_absolute(link_lenta)

news_links = root.xpath('''(//div[@class="row"]//div[@class="first-item"]/h2 | 
                            //div[@class="row"]//div[@class="item"])
                            /a/@href''')

news_text = root.xpath('''(//div[@class="row"]//div[@class="first-item"]/h2 | 
                            //div[@class="row"]//div[@class="item"])
                            /a/text()''')

for i in range(len(news_text)):
    news_text[i] = news_text[i].replace(u'\xa0', u' ')

news_date = []

for item in news_links:
    request = requests.get(item)
    root = html.fromstring(request.text)
    date = root.xpath('//time[@class="g-time"]/@datetime')
    news_date.extend(date)

for item in list(zip(news_text, news_date, news_links)):
    news_dict = {}
    for key, value in zip(keys, item):
        news_dict[key] = value

    news_dict['sourse'] = 'lenta.ru'
    news.append(news_dict)

request = requests.get(link_lenta)

root = html.fromstring(request.text)
root.make_links_absolute(link_lenta)

news_links = root.xpath('''(
                            //div[@class="row"]//div[@class="b-feature__header"])
                            /a/@href''')
news_text = root.xpath('''(
                            //div[@class="row"]//div[@class="b-feature__header"])
                            /a/text()''')
news_date = root.xpath('''(
                            //div[@class="row"]//div[@class="g-date"])
                            /time/text()''')

for i in range(len(news_text)):
    news_text[i] = news_text[i].replace(u'\xa0', u' ')



for item in list(zip(news_text, news_date, news_links)):
    news_dict = {}
    for key, value in zip(keys, item):
        news_dict[key] = value

    news_dict['sourse'] = 'lenta.ru'
    news.append(news_dict)

request = requests.get(link_lenta)

root = html.fromstring(request.text)
root.make_links_absolute(link_lenta)

news_links = root.xpath('''(
                            //div[@class="row"]//div[@class="titles"]/h3)
                            /a/@href''')
news_text = root.xpath('''(
                            //div[@class="row"]//div[@class="titles"]/h3)
                            /a/span/text()''')
news_date = root.xpath('''(
                            //div[@class="row"]//div[@class="info g-date item__info"])
                            /span/text()''')

now = datetime.now()

for i in range(len(news_text)):
    news_text[i] = news_text[i].replace(u'\xa0', u' ')

for i in range(len(news_date)):
    news_date[i] = news_date[i].replace(u'Сегодня', now.strftime("%d-%m-%Y"))

for item in list(zip(news_text, news_date, news_links)):
    news_dict = {}
    for key, value in zip(keys, item):
        news_dict[key] = value

    news_dict['sourse'] = 'lenta.ru'
    news.append(news_dict)

# mail.ru

link_mail_ru = 'https://news.mail.ru/'

request = requests.get(link_mail_ru)

root = html.fromstring(request.text)
root.make_links_absolute(link_mail_ru)

news_links = root.xpath('''(//td[@class='daynews__main']|
                               //td[@class='daynews__items']|
                               //li[@class='list__item']|
                               //div[@class='cols__wrapper']//span[@class='cell'])
                               //a/@href''')

news_text = root.xpath('''(//td[@class='daynews__main']//span[@class='photo__title photo__title_new photo__title_new_hidden js-topnews__notification']|
                               //td[@class='daynews__items']//span[@class='photo__title photo__title_new photo__title_new_hidden js-topnews__notification']|
                               //li[@class='list__item']//a|
                               //div[@class='cols__wrapper']//span[@class='cell']//a/span)
                               //text()''')

for i in range(len(news_text)):
    news_text[i] = news_text[i].replace(u'\xa0', u' ')


news_date = []

for item in news_links:
    request = requests.get(item)
    root = html.fromstring(request.text)
    date = root.xpath('//span[@class="note__text breadcrumbs__text js-ago"]/@datetime')
    news_date.extend(date)

for i in range(len(news_date)):
        news_date[i] = news_date[i].replace(u'+03:00', u'')
        news_date[i] = news_date[i].replace(u'T', u', ')

news_sourse = []
for item in news_links:
    request = requests.get(item)
    root = html.fromstring(request.text)
    sourse = root.xpath('''//span[@class='breadcrumbs__item']//span[@class='note']
                           //a//span/text()''')
    news_sourse.extend(sourse)

for item in list(zip(news_text, news_date, news_links, news_sourse)):
    news_dict = {}
    for key, value in zip(keys, item):
       news_dict[key] = value

    news.append(news_dict)

# yandex.ru

link_yandex_ru = 'https://yandex.ru/news/'

request = requests.get(link_yandex_ru)

root = html.fromstring(request.text)
root.make_links_absolute(link_yandex_ru)

news_links = root.xpath('''//div[@class='mg-grid__col mg-grid__col_xs_12 mg-grid__col_sm_9']
                               //div[@class='mg-card__text']//a/@href''')

news_text = root.xpath('''//div[@class='mg-grid__col mg-grid__col_xs_12 mg-grid__col_sm_9']
                               //div[@class='mg-card__text']//a/h2/text()''')

for i in range(len(news_text)):
    news_text[i] = news_text[i].replace(u'\xa0', u' ')


news_date = root.xpath('''//div[@class='mg-card-footer__left']//span/text()''')

now = datetime.now()
yesterday = datetime.now() - timedelta(days=1)
now = now.strftime(date_format)
yesterday = yesterday.strftime(date_format)

for i in range(len(news_date)):
    if news_date[i].find('вчера') != -1:
        news_date[i] = news_date[i].replace(u'вчера в ', yesterday+', ')
    elif news_date[i].find('в') != -1:
        news_date[i] = news_date[i]
    else:
        news_date[i] = now + ', ' + news_date[i]

news_sourse = root.xpath('''//div[@class='mg-card-footer__left']
                             //span[@class='mg-card-source__source']//a/text()''')

for item in list(zip(news_text, news_date, news_links, news_sourse)):
    news_dict = {}
    for key, value in zip(keys, item):
       news_dict[key] = value

    news.append(news_dict)

MONGO_URI = "127.0.0.1:27017"
MONGO_DB = "News_new"

with MongoClient(MONGO_URI) as client:
    db = client[MONGO_DB]
    News_db = db.News_news

    News_db.insert_many(news)
    pprint(News_db)

df = pd.DataFrame(news)
print(df)