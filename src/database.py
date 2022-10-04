#!/bin/env python3.9

import pymongo
import os

from dotenv import load_dotenv

load_dotenv()

db_uri = os.getenv('MONGO_DB_URI')
db_name = os.getenv('MONGO_DB_NAME')
db_collection = os.getenv('MONGO_COLLECTION_NAME')


def get_database() -> pymongo.database.Database:
    try: 
pymongo.MongoClient(db_uri, retryWrites=False)
    return 


def get_data(collection: pymongo.collection.Collection):
    return None


def insert_data(collection: pymongo.collection.Collection):
    collection.insert_one({"BookTitle": "War and peace"})


if __name__ == "__main__":
    mongo_client = get_database()
    # print(type())

    database = mongo_client[db_name]
    collection = database[db_collection]

    insert_data(collection)

    # data = get_data

    # insert sample data
    # insert_data(db_collection)
