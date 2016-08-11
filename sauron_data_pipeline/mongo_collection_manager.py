from pymongo import MongoClient
import sys
import json

class MongoCollectionManager:
    """
    MongoCollectionManager provides wraps find_documents and remove_documents from MongoClient
    """
    def __init__(self, mongodb_uri, database, collection):
        self.conn = MongoClient(mongodb_uri)
        self.db = self.conn[database]
        self.collection = self.db[collection]

    def find_documents(self, id_field='_id', last_max_id=0, cursor_limit=1000):
        """
        :param id_field: numeric, ever increasing index of documents
        :param last_max_id: greatest id_field value of the last retrieved set of documents
        :param cursor_limit: maximum number of documents to retrieve
        :return: list of documents
        """
        cursor = self.collection.find({id_field: {'$gt': last_max_id}}).limit(cursor_limit)
        return list(cursor)

    def remove_documents(self, id_field='_id', last_max_id=0):
        """
        :param id_field: numeric index of documents
        :param last_max_id: greatest id_field removed from the collection
        :return: result from self.collection.remove
        """
        return self.collection.remove({id_field: {'lte': last_max_id}})

if __name__ == '__main__':

    with open('config.json') as config_file:
        config = json.load(config_file)

    to_get = 10
    to_remove = 1
    if len(sys.argv[1:]) == 1:
        to_get = int(sys.argv[1])
    if len(sys.argv[2:]) == 1:
        to_remove = int(sys.argv[2])

    db_uri = config["local_mongodb"]["uri"]
    db = config["local_mongodb"]["source_db"]
    coll = config["local_mongodb"]["source_collections"]["profiles"]

    mcm = MongoCollectionManager(db_uri, db, coll)

    res = mcm.find_documents(last_max_id=to_get)
    print(res)

    rem = mcm.remove_documents(last_max_id=to_remove)
    print("Docs removed: %s" % (rem['n']))
