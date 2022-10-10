#!/bin/env python3.9

import pymongo
# import os

# from dotenv import load_dotenv

# load_dotenv()

# db_uri = os.getenv('MONGO_DB_URI')
# db_name = os.getenv('MONGO_DB_NAME')
# db_collection = os.getenv('MONGO_COLLECTION_NAME')


class MongoDB():
    def __init__(self, db_uri, db_name, db_user_collection, db_text_collection):
        self._db_uri = db_uri
        self._db_name = db_name
        # there can be multiple collections
        # too much text variables, have to be objects
        self._db_user_collection = db_user_collection
        self._db_text_collection = db_text_collection
        # too complex
        self._db = None
        self.get_database()

    # def get_database(self) -> pymongo.database.Database:
    def get_database(self) -> None:
        try:
            mongo_client = pymongo.MongoClient(self._db_uri, retryWrites=False)
            # return mongo_client[self._db_name]
            # mistake here
            self._db = mongo_client[self._db_name]

        except Exception as e:
            print(e)
            exit(1)

    def insert_new_user_data(self, owner_id) -> None:
        try:
            self._db_user_collection.insert_one(
                {
                    "OwnerID": owner_id,
                    "BookTitle": "War and peace",
                }
            )

        except Exception as e:
            print(e)


def insert_data(collection: pymongo.collection.Collection):
    try:
        collection.insert_one(
            {
                "OwnerID": 1023,
                "BookTitle": "War and peace",
            }
        )
    except Exception as e:
        print(e)




# if __name__ == "__main__":
#     database = get_database()
#     # print(type())

#     collection = database[db_collection]

#     insert_data(collection)

#     # data = get_data

#     # insert sample data
#     # insert_data(db_collection)
