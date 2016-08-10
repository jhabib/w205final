from __future__ import absolute_import
from kafka import KafkaConsumer
import avro
import avro.schema
import io


class KafkaAvroConsumer:

    def __init__(self):
        pass

    @staticmethod
    def create_consumer(topic, group_id, bootstrap_uri):
        return KafkaConsumer(topic, group_id=group_id, bootstrap_servers=[bootstrap_uri])

    @staticmethod
    def decode_message(schema, message):
        bytes_reader = io.BytesIO(message.value)
        decoder = avro.io.BinaryDecoder(bytes_reader)
        reader = avro.io.DatumReader(schema)
        return reader.read(decoder)

