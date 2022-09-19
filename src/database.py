import pymongo


def get_collection():
    client = pymongo.MongoClient()
    db = client["database"]
    col = db["transactions"]
    return col
