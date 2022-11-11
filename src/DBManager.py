#!/bin/env python3.9

from re import T
import pymongo


class MongoDBManager():
    def __init__(self, db_uri, db_name, db_user_collection_name, db_book_collection_name):
        self._db_uri = db_uri
        # self._db_name = db_name
        self._db = self._get_database(db_name)
        self._db_user_collection = self._get_collection(db_user_collection_name)
        self._db_book_collection = self._get_collection(db_book_collection_name)

    # private method
    def _get_database(self, db_name) -> pymongo.database.Database:
        try:
            mongo_client = pymongo.MongoClient(self._db_uri, retryWrites=False)
            # return mongo_client[self._db_name]
            # mistake here
            return mongo_client[db_name]

        except Exception as e:
            print(e)
            exit(1)

    # private method
    def _get_collection(self, collection_name) -> pymongo.collection.Collection:
        return self._db[collection_name]

    # must take a Client instance as argument
    # def insert_new_user(self, user_id) -> None:
    def insert_new_user(self, user) -> None:
        # TODO: add a check if user already exists
        try:
            self._db_user_collection.insert_one(
                user.__dict__,
            )

        except pymongo.errors.DuplicateKeyError:
            return "User already exists in database"

        except Exception as e:
            return e
        
        return "User was successfully added to database"
    
    def update_user(self, user):
        try:
            self._db_user_collection.update_one(
                {
                    "_id": user._id,
                },
                {
                    "$set": user.__dict__,
                }
            )

        except Exception as e:
            print(e)
            return e

    # inserts new book
    # def insert_book(self, book_instance) -> None:
    # book_content = transalted data from epub to txt
    # TODO: no same title books
    def insert_book(self, book) -> bool:
        try:
            self._db_book_collection.insert_one(
                book.__dict__,
            )
            return True

        except Exception as e:
            print(e)

    def get_owner_files(self, owner_id) -> None:
        """
            return titles(anything else?) of the uploaded books per user
        """
        # TODO: function must have only one db request
        try:
            return self._db_book_collection.find(
                {
                    "owner_id": owner_id,
                }
            )

        except Exception as e:
            print(e)
    
    def modify_book_field(self, book) -> None:
        return None
