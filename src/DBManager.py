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
                    # new user always has zero books
                    "OwnerBooks": [],
                }
            )

        except Exception as e:
            print(e)

    # inserts new book
    # def insert_book(self, book_instance) -> None:
    # book_content = transalted data from epub to txt
    def insert_book(self, owner_id, book_title, book_content) -> None:
        try:
            self._db_text_collection.insert_one(
                {
                    "OwnerID": owner_id,
                    "BookTitle": book_title,
                    "TextData": book_content,
                }
            )

        except Exception as e:
            print(e)

    # return titles of the uploaded books per user
    def get_owner_files(self, owner_id) -> None:
        try:
            # must have only one return
            quantity = self._db_text_collection.count_documents(
                {
                    "OwnerID": owner_id,
                }
            )
            if quantity > 0:
                return self._db_text_collection.find(
                    {
                        "OwnerID": owner_id,
                    }
                )
            return None

        except Exception as e:
            print(e)
