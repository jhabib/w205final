# class to write data to Google BigQuery
# uses the kafka consumer (SauronConsumer) to get json from kafka

import json
import time
import uuid
from threading import Thread

from googleapiclient import discovery

from kafka.sauron_consumer import SauronConsumer


class SauronBigQueryManager:
    """
    Handles row formatting and inserts for Bigquery
    """
    def __init__(self, bigquery, project_id, dataset_id, table_name, num_retries=5):
        self.bigquery = bigquery
        self.project_id = project_id
        self.dataset_id = dataset_id
        self.table_name = table_name
        self.num_retries = num_retries

    # format rows to bigquery friendly
    @staticmethod
    def format_rows(rows):
        return [{'json': row, 'insertId': str(uuid.uuid4())} for row in rows]

    # stream_row_to_bigquery taken from Google's BigQuery tutorial
    def stream_row_to_bigquery(self, rows):
        insert_all_data = {
            'rows': self.format_rows(rows)
        }
        response = self.bigquery.tabledata().insertAll(projectId=self.project_id, datasetId=self.dataset_id,
                                                       tableId=self.table_name,
                                                       body=insert_all_data).execute(num_retries=self.num_retries)
        return response, self.table_name


class RowGetter:
    """
    Provides a callback for the Kafka consumer
    Handles putting message to a shared Queue
    """
    def __init__(self, shared_queue):
        self.shared_queue = shared_queue

    def fill_queue(self, m):
        self.shared_queue.put(m)

    def get_row(self, m):
        self.fill_queue(json.loads(m))


class MessageBatch:
    """
    Pops messages from shared Queue and batches them in memory; Sends batch to a callback.
    This is not safe because we can drop messages equal to batch size.
    In production we should get batches of messages from Kafka and send them onward in chunks,
    or store messages to a file and batch from there
    """
    def __init__(self, shared_queue, send_callback, batch_size=100):
        self.shared_queue = shared_queue
        self.send_callback = send_callback
        self.batch_size = batch_size

    def batch_rows(self):
        this_batch = []
        while True:
            while len(this_batch) < self.batch_size and self.shared_queue.qsize() > 0:
                this_batch.append(self.shared_queue.get())
                print('got a message')
                time.sleep(0.001)

            if len(this_batch) >= self.batch_size:
                r, t = self.send_callback(this_batch)
                this_batch = []  # clean up the batch after sending the messages
                print('Table name: %s' % (t))
                print('Response: %s' % (r))
                time.sleep(0.001)


class SetupBigQueryHandler:
    """
    SetupBigQueryHandler sets up:
    Kafka consumer to get data from the specified Kafka topic
    Row getter callback for the Kafka consumer thread; this also puts data into the shared Queue
    Shared Queue to temporarily hold Kafka messages for batch processing
    Shared Queue consumer thread to batch up messages and insert into BigQuery
    Bigquery connection object
    Bigquery wrapper to insert data into bigquery
    """

    def __init__(self, projectid, datasetid, tablename, numretries, creds,
                 kafkauri, kafkatopic, shared_queue, batch_size):
        self.project_id = projectid
        self.dataset_id = datasetid
        self.table_name = tablename
        self.num_retries = numretries
        self.credentials = creds
        self.kafka_uri = kafkauri
        self.kafka_topic = kafkatopic
        self.shared_queue = shared_queue
        self.batch_size = batch_size

    def setup_bigquery_handler(self):
        # Create a bigquery object
        bigquery = discovery.build('bigquery', 'v2', credentials=self.credentials)

        # Create an instance of the Query manager wrapper
        sbqm = SauronBigQueryManager(bigquery, self.project_id, self.dataset_id, self.table_name, self.num_retries)
        mb = MessageBatch(self.shared_queue, sbqm.stream_row_to_bigquery, self.batch_size)
        rg = RowGetter(self.shared_queue)

        batch_worker = Thread(target=mb.batch_rows)
        batch_worker.setDaemon(True)
        batch_worker.start()

        threads = [
            SauronConsumer(self.kafka_uri, self.kafka_topic, rg.get_row)  # Run Kafka consumer in a thread
        ]
        for t in threads:
            t.start()
            t.join()
        time.sleep(10)


def handler_setup(topic, table, shared_queue, config, credentials, retries=2, batch_size=100):
    project_id = config["bigquery"]["projectid"]
    dataset_id = config["bigquery"]["dataset"]
    table_name = config["bigquery"]["tables"][table]

    kafka_uri = config["kafka"]["uri"]
    kafka_topic = config["kafka"]["topics"][topic]

    handler = SetupBigQueryHandler(project_id, dataset_id, table_name, retries, credentials,
                                           kafka_uri, kafka_topic, shared_queue, batch_size)
    handler.setup_bigquery_handler()


def main():

    pass

if __name__ == '__main__':
    main()

