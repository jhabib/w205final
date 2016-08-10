from __future__ import absolute_import
from kafka import KafkaProducer
from avro.io import DatumWriter, BinaryEncoder
import avro
import avro.schema
import io
import time
import random


class KafkaAvroProducer:

    def __init__(self, kafka_uri):
        self.uri = kafka_uri
        self.producer = KafkaProducer(bootstrap_servers=[self.uri])

    @staticmethod
    def encode_messages(schema_path, messages):
        raw_bytes = []
        schema = avro.schema.parse(open(schema_path).read())
        for m in messages:
            writer = DatumWriter(schema)
            bytes_writer = io.BytesIO()
            encoder = BinaryEncoder(bytes_writer)
            writer.write(m, encoder)
            raw_bytes.append(bytes_writer.getvalue())
        return raw_bytes

    def produce_messages(self, topic, messages):
        self.producer.send(topic, messages)


if __name__ == '__main__':
    import json
    print("producing message")

    try:
        producer = KafkaAvroProducer('localhost:9092')
    except Exception as e:
        print(e.message)

    # message = {"_id": "idid",
    #            "Topic": "profiles",
    #            "Key": "G2S_Key",
    #            "Value": "json_encoded_string"}

    # jd = json.dumps(message)

    # message_bytes = producer.encode_messages(r"./avro_schemas/profile.avsc", message)
    # producer.produce_messages("profiles", message_bytes)

    while True:
        message = {"_id": str(random.randint(0, 100)),
                   "Topic": "profiles",
                   "Key": "G2S_Key",
                   "Value": "json_encoded_string"}

        jd = json.dumps(message)
        producer.produce_messages("profiles", jd)
        time.sleep(0.001)

