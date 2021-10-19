import pymongo

from analyzer import DB_URI, DB_NAME, DB_COLLECTION_NAME


def get_mongo_collection():
    server = pymongo.MongoClient(DB_URI)
    db = server[DB_NAME]
    collection = db[DB_COLLECTION_NAME]
    return collection
