#!/bin/env python3.9

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
    def insert_new_user(self, user) -> str:
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

    def get_user(self, uid) -> None:
        try:
            return self._db_user_collection.find_one({"_id": uid})

        except Exception as e:
            print(e)

    def get_all_users(self) -> None:
        try:
            return self._db_user_collection.find({})

        except Exception as e:
            print(e)

    def get_current_users_ids(self) -> None:
        try:
            return self._db_user_collection.find(
                {
                    "using_bot_flag": True,
                }
            )

        except Exception as e:
            print(e)

    def update_user(self, user, query=None):
        try:
            if query is None:
                query = user.__dict__
            self._db_user_collection.update_one(
                {
                    "_id": user._id,
                },
                {
                    "$set": query
                }
            )
            return True

        except Exception as e:
            print(e)
            return False

    # inserts new book if no such title already exists
    def insert_book(self, book) -> bool:
        try:
            # switch with update method later
            res = self._db_book_collection.count_documents(
                {
                    "title": book.title
                }
            )
            if res > 0:
                return False

            self._db_book_collection.insert_one(
                book.__dict__,
            )
            return True

        except Exception as e:
            print(e)
            return False

    # this can return none
    def get_user_books(self, owner_id) -> None:
        """
            return titles(anything else?) of the uploaded books per user
        """
        try:
            return self._db_book_collection.find(
                {
                    "owner_id": owner_id,
                }
            )

        except Exception as e:
            print(e)

    def get_shared_books(self) -> None:
        """
            return titles(anything else?) of the uploaded books per user
        """
        try:
            return self._db_book_collection.find(
                {
                    "shared": True,
                }
            )

        except Exception as e:
            print(e)

    def get_max_book_index(self) -> int:
        """
            return titles(anything else?) of the uploaded books per user
        """
        # TODO: function must have only one db request
        try:
            doc = self._db_book_collection.find_one(sort=[("index", -1)])
            if doc is None:
                return 1
            return doc.get("index") + 1

        except Exception as e:
            print(e)

    def get_book(self, book_index, query=None):
        """
            return titles(anything else?) of the uploaded books per user
        """
        # TODO: function must have only one db request
        try:
            if query is None:
                query = {"index": book_index}
            doc = self._db_book_collection.find_one(
                query
            )
            return doc

        except Exception as e:
            print(e)

    def get_all_books(self) -> None:
        try:
            return self._db_book_collection.find({})

        except Exception as e:
            print(e)

    def update_book(self, book, query=None):
        try:
            if query is None:
                query = book.__dict__
            self._db_book_collection.update_one(
                {
                    "_id": book._id,
                },
                {
                    "$set": query
                }
            )
            return True

        except Exception as e:
            print(e)
            return False
