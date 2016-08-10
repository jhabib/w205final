import threading
import logging
import time
import json

from mongo_collection_manager import MongoCollectionManager
from kafka import KafkaProducer
from pymongo import MongoClient


class SauronProducer(threading.Thread):
    daemon = True

    def __init__(self, mongodb_uri, source_db, source_collection,
                 counters_db, counters_collection,
                 kafka_uri, kafka_topic):

        threading.Thread.__init__(self)

        self.COUNTER_CONN = MongoClient(mongodb_uri)
        self.COUNTER_DB = self.COUNTER_CONN[counters_db]
        self.COUNTER_COLLECTION = self.COUNTER_DB[counters_collection]
        self.COUNTER_FIELD = 'value'

        self.SOURCE_URI = mongodb_uri
        self.SOURCE_DB = source_db
        self.SOURCE_COLLECTION = source_collection

        self.MCM = MongoCollectionManager(self.SOURCE_URI, self.SOURCE_DB, self.SOURCE_COLLECTION)

        self.KAFKA_URI = kafka_uri
        self.KAFKA_TOPIC = kafka_topic

        self.SOURCE_FIELD = '_id'
        self.LAST_MSG_ID = 0
        self.CURSOR_LIMIT = 5000

        self.GET_INTERVAL = 0.001 # seconds
        self.SEND_INTERVAL = 0.001 # seconds

        self.PRODUCER = KafkaProducer(bootstrap_servers=[self.KAFKA_URI],
                                      value_serializer=lambda v: json.dumps(v).encode('utf-8'))

    def run(self):
        # get the last message id that we know was sent
        cur = self.COUNTER_COLLECTION.find_one(sort=[(self.COUNTER_FIELD, -1)])
        if cur is not None:
            # set the LAST_MSG_ID to value from DB
            self.LAST_MSG_ID = cur[self.COUNTER_FIELD]

        res_id = 0
        while True:
            print('\ngetting data from %s.%s' % (self.SOURCE_DB, self.SOURCE_COLLECTION))
            res = self.MCM.find_documents(self.SOURCE_FIELD, self.LAST_MSG_ID, self.CURSOR_LIMIT)
            if len(res) > 0:  # don't send an empty message
                for r in res:
                    res_id = r[self.SOURCE_FIELD]
                    try:
                        print('\nsending message to %s on %s' % (self.KAFKA_TOPIC, self.KAFKA_URI))
                        self.PRODUCER.send(self.KAFKA_TOPIC, r)
                    except Exception as e:
                        print('Exception occurred when sending data to Kafka')
                        print(e.message)
                    time.sleep(self.SEND_INTERVAL) # send message interval

            if res_id > self.LAST_MSG_ID:
                self.LAST_MSG_ID = res_id
                try:
                    self.COUNTER_COLLECTION.insert_one({self.COUNTER_FIELD: self.LAST_MSG_ID})
                except Exception as e:
                    print('Exception occurred when writing to %s.%s' % (self.COUNTER_DB, self.COUNTER_COLLECTION))
                    print(e.message)
            time.sleep(self.GET_INTERVAL)  # get from source interval


# Launch Kafka producers for profiles and events
def launch_producer_threads():
    with open('config.json') as config_file:
        config = json.load(config_file)

    kafka_uri = config["kafka"]["uri"]
    profiles_kafka_topic = config["kafka"]["topics"]["profiles"]
    events_kafka_topic = config["kafka"]["topics"]["events"]

    mongodb_uri = config["local_mongodb"]["uri"]
    source_db = config["local_mongodb"]["source_db"]
    profiles_collection = config["local_mongodb"]["source_collections"]["profiles"]
    events_collection = config["local_mongodb"]["source_collections"]["events"]

    counters_db = config["local_mongodb"]["counters_db"]
    profile_counters_collection = config["local_mongodb"]["counters_collection"]["profiles"]
    event_counters_collection = config["local_mongodb"]["counters_collection"]["events"]

    threads = [
        SauronProducer(mongodb_uri, source_db, profiles_collection,
                       counters_db, profile_counters_collection,
                       kafka_uri, profiles_kafka_topic),

        SauronProducer(mongodb_uri, source_db, events_collection,
                       counters_db, event_counters_collection,
                       kafka_uri, events_kafka_topic)
    ]
    for t in threads:
        t.start()
    t.join()
    time.sleep(10)

if __name__ == "__main__":
    print("running producer ...")

    logging.basicConfig(
        format='%(asctime)s.%(msecs)s:%(name)s:%(thread)d:%(levelname)s:%(process)d:%(message)s',
        level=logging.INFO
    )
    launch_producer_threads()
