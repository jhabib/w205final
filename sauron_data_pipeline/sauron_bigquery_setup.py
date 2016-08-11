# # file that uses the bigquery-python library
# # to insert streaming data into biqquery
# import json
# import logging
# import time
# import uuid
#
# from bigquery import get_client
# from flatten_json import flatten_json
# from pandas.io.json import json_normalize
#
# from sauron_consumer import SauronConsumer
#
# logging.basicConfig()
#
# project_id = 'sauronbigquery'
# dataset = 'sauron'
#
# table = 'gamePlayProfiles'
# # gameplay_profiles_schema = []
# # schemas = {'gameplay_profiles': gameplay_profiles_schema}
#
# key = 'C:\users\sp4\google drive\googlekeys\SauronBigQuery-a8483044e8cc.json'
#
# client = get_client(json_key_file=key, readonly=False)
#
# # create dataset
# # if dataset not in client.get_datasets():
# #     res = client.create_dataset(dataset, str(dataset))
# #     print(res)
#
# # create tables
# # res = [client.create_table(dataset, table, gameplay_profiles_schema) for table in tables if not client.check_table(dataset, table)]
# # print(res)
#
#
# def insert_callback(m):
#
#     try:
#         obj = json.loads(m)
#         # print(obj['_id'])
#     except ValueError as e:
#         print(e.message)
#     # print(type(obj))
#
#     # print(flatten_json.flatten_json(obj))
#
#     norm = json_normalize(obj)
#     dic_flattened = [flatten_json(d) for d in norm]
#     print(dic_flattened)
#     insert_all_data = [{
#             'json': obj,
#             # Generate a unique id for each row so retries don't accidentally
#             # duplicate insert
#             'insertId': str(uuid.uuid4()),
#         }]
#     # inserted = client.push_rows(dataset, table, insert_all_data)
#     # print(str(inserted))
#
#
# def main():
#     KAFKA_URI = 'localhost:9092'
#     KAFKA_TOPIC = 'profiles'
#     threads = [
#         SauronConsumer(KAFKA_URI, KAFKA_TOPIC, insert_callback)
#     ]
#     for t in threads:
#         t.start()
#         t.join()
#     time.sleep(10)
#
#
# if __name__ == '__main__':
#     main()
#
