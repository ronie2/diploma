from config.conf import mongo_cfg
from copy import deepcopy
from pymongo import MongoClient


class DatabaseAgent:
    def __init__(self, db_name=mongo_cfg["db_name"]):
        self.client = MongoClient()
        self.db = self.client[db_name]

    def insert_one(self, collection_name, data_to_add):
        collection = self.db[collection_name]
        inserted = collection.insert_one(deepcopy(data_to_add))
        return inserted

    def find_all(self, collection_name):
        return self.find(collection_name)

    def find(self, collection_name, pattern=None):
        collection = self.db[collection_name]
        return collection.find(pattern)

    def find_one(self, collection_name, pattern=None):
        collection = self.db[collection_name]
        return collection.find_one(pattern)

    def delete_one(self, collection_name, pattern=None):
        collection = self.db[collection_name]
        return collection.delete_one(pattern)