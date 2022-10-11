#!/bin/env python3.9

import pymongo


class MongoDBManager():
    def __init__(self, db_uri, db_name, db_user_collection_name, db_text_collection_name):
        self._db_uri = db_uri
        # self._db_name = db_name
        self._db = self._get_database(db_name)
        self._db_user_collection = self._get_collection(db_user_collection_name)
        self._db_text_collection = self._get_collection(db_text_collection_name)

    # private
    def _get_database(self, db_name) -> pymongo.database.Database:
        try:
            mongo_client = pymongo.MongoClient(self._db_uri, retryWrites=False)
            # return mongo_client[self._db_name]
            # mistake here
            return mongo_client[db_name]

        except Exception as e:
            print(e)
            exit(1)

    def _get_collection(self, collection_name) -> pymongo.collection.Collection:
        return self._db[collection_name]

    # must take a Client instance as argument
    def insert_new_user(self, owner_id) -> None:
        try:
            self._db_user_collection.insert_one(
                {
                    "OwnerID": owner_id,
                    "BookTitle": "War and peace",
                }
            )

        except Exception as e:
            print(e)

    def insert_text_data(self, owner_id, text_data) -> None:
        try:
            self._db_text_collection.insert_one(
                {
                    "OwnerID": owner_id,
                    "TextData": text_data,
                }
            )

        except Exception as e:
            print(e)

    def get_owner_files(self, ownder_id) -> None:
        try:
            return self._db_text_collection.find(
                {
                    "OwnerID": ownder_id,
                }
            )
        except Exception as e:
            print(e)
