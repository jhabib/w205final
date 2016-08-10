from pymongo import MongoClient
import sys
import json

class MongoCollectionManager:

    def __init__(self, mongodb_uri, database, collection):
        self.conn = MongoClient(mongodb_uri)
        self.db = self.conn[database]
        self.collection = self.db[collection]

    def find_documents(self, id_field='_id', last_max_id=0, cursor_limit=1000):
        cursor = self.collection.find({id_field: {'$gt': last_max_id}}).limit(cursor_limit)
        return list(cursor)

    def remove_documents(self, id_field='_id', last_max_id=0):
        rem = self.collection.remove({id_field: {'lte': last_max_id}})
        return rem

if __name__ == '__main__':

    with open('config.json') as config_file:
        config = json.load(config_file)

    to_get = 10
    to_remove = 1
    if len(sys.argv[1:]) == 1:
        to_get = int(sys.argv[1])
    if len(sys.argv[2:]) == 1:
        to_remove = int(sys.argv[2])

    # db_uri = "localhost:27017"
    # db = 'sauron'
    # coll = 'profile'

    db_uri = config["local_mongodb"]["uri"]
    db = config["local_mongodb"]["source_db"]
    coll = config["local_mongodb"]["source_collections"]["profiles"]

    mcm = MongoCollectionManager(db_uri, db, coll)

    res = mcm.find_documents(last_max_id=to_get)
    print(res)

    rem = mcm.remove_documents(last_max_id=to_remove)
    print("Docs removed: %s" % (rem['n']))
