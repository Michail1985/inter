# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from pymongo import MongoClient
MONGO_URL = "localhost:27017"


class BookparserPipeline:
    def __init__(self):
        self.client = MongoClient(MONGO_URL)
        self.db = self.client['books']

    def process_item(self, item, spider):
        collection = self.db[spider.name]
        #collection.insert_one(item)
        collection.update_one({'link': item['link']}, {"$set": item}, upsert=True)
        print()
        return item
