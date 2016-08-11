import threading
import logging
import time
import json

from mongo_collection_manager import MongoCollectionManager
from kafka import KafkaProducer
from pymongo import MongoClient


class SauronProducer(threading.Thread):
    """
    SauronProducer gets a set of documents from a MongoDB collection
    And sends them over to a Kafka topic
    """
    daemon = True

    def __init__(self, mongodb_uri, source_db, source_collection,
                 counters_db, counters_collection,
                 kafka_uri, kafka_topic):

        threading.Thread.__init__(self)

        self.counter_conn = MongoClient(mongodb_uri)
        self.counter_db = self.counter_conn[counters_db]
        self.counter_collection = self.counter_db[counters_collection]
        self.counter_field = 'value'

        self.source_uri = mongodb_uri
        self.source_db = source_db
        self.source_collection = source_collection

        self.mcm = MongoCollectionManager(self.source_uri, self.source_db, self.source_collection)

        self.kafka_uri = kafka_uri
        self.kafka_topic = kafka_topic

        self.source_field = '_id'
        self.last_msg_id = 0
        self.cursor_limit = 5000

        self.get_interval = 0.001 # seconds
        self.send_interval = 0.001 # seconds

        self.kafka_producer = KafkaProducer(bootstrap_servers=[self.kafka_uri],
                                            value_serializer=lambda v: json.dumps(v).encode('utf-8'))

    def run(self):
        """
        Override the run method for threading.Thread
        :return: None
        """
        # get the last message id that we know was sent
        cur = self.counter_collection.find_one(sort=[(self.counter_field, -1)])
        if cur is not None:
            # set the last_msg_id to value from DB
            self.last_msg_id = cur[self.counter_field]

        res_id = 0
        while True:
            print('\ngetting data from %s.%s' % (self.source_db, self.source_collection))
            res = self.mcm.find_documents(self.source_field, self.last_msg_id, self.cursor_limit)
            if len(res) > 0:  # don't send an empty message
                for r in res:
                    res_id = r[self.source_field]
                    try:
                        print('\nsending message to %s on %s' % (self.kafka_topic, self.kafka_uri))
                        self.kafka_producer.send(self.kafka_topic, r)
                    except Exception as e:
                        print('Exception occurred when sending data to Kafka')
                        print(e.message)
                    time.sleep(self.send_interval)  # send message interval

            if res_id > self.last_msg_id:  # keep track of the last id sent to Kafka
                self.last_msg_id = res_id
                try:
                    self.counter_collection.insert_one({self.counter_field: self.last_msg_id})
                except Exception as e:
                    print('Exception occurred when writing to %s.%s' % (self.counter_db, self.counter_collection))
                    print(e.message)
            time.sleep(self.get_interval)  # get from source interval


# Launch Kafka producers for profiles and events
def launch_producer_threads():
    """
    Start a producer for each topic on its own thread
    :return: None
    """
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
