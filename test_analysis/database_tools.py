from copy import deepcopy
from pymongo import MongoClient
from conf import mongo_cfg


class DatabaseAgent:
    def __init__(self, db_name=mongo_cfg["db_name"]):
        self.client = MongoClient()
        self.db = self.client[db_name]

    def insert_one(self, collection_name, data_to_add):
        collection = self.db[collection_name]
        return collection.insert_one(deepcopy(data_to_add))

    def insert_many(self, collection_name, data_to_add, ordered):
        collection = self.db[collection_name]
        return collection.insert_many(data_to_add, ordered=ordered)

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

    def create_index(self, collection_name, key=None):
        collection = self.db[collection_name]
        return collection.create_index(key)
