from kafka import KafkaConsumer
import threading
import logging
import time
import json


class SauronConsumer(threading.Thread):
    daemon = True

    def __init__(self, kafka_uri, topic, message_callback):

        threading.Thread.__init__(self)

        self.KAFKA_URI = kafka_uri
        self.KAFKA_TOPIC = topic

        self.CALLBACK = message_callback

        self.SEND_INTERVAL = 0.01 # seconds

    def run(self):
        consumer = KafkaConsumer(bootstrap_servers=[self.KAFKA_URI],
                                 auto_offset_reset='earliest')
        # ,value_deserializer=lambda m: json.loads(m.decode('utf-8'))
        consumer.subscribe([self.KAFKA_TOPIC])

        # pass a queue in here
        for m in consumer:
            self.CALLBACK(m.value)
            time.sleep(self.SEND_INTERVAL)


# Test callback
# prints a message received from Kafka
def m_callback(m):
    print('executing callback...')
    print(m)

# Test the SauronConsumer class
def test():
    with open('config.json') as config_file:
        config = json.load(config_file)

    kafka_uri = config["kafka"]["uri"]
    kafka_topic = config["kafka"]["topics"]["events"]

    threads = [
        SauronConsumer(kafka_uri, kafka_topic, m_callback)
    ]
    for t in threads:
        t.start()
        t.join()
    time.sleep(10)

if __name__ == "__main__":
    print("running consumer ...")

    logging.basicConfig(
        format='%(asctime)s.%(msecs)s:%(name)s:%(thread)d:%(levelname)s:%(process)d:%(message)s',
        level=logging.INFO
    )
    test()
