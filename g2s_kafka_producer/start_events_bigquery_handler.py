from sauron_bigquery_manager import *
from multiprocessing import Queue
from oauth2client.client import GoogleCredentials

if __name__ == '__main__':
    with open('config.json') as config_file:
        config = json.load(config_file)

    events_shared_queue = Queue()
    events_topic = 'events'
    events_table = 'events'

    # GOOGLE_APPLICATION_CREDENTIALS environment variable must be set
    # And it must point to the service account key (.json)
    credentials = GoogleCredentials.get_application_default()

    print('setting up bigquery handler for %s' % (events_topic))
    handler_setup(events_topic, events_table, events_shared_queue, config, credentials, 5, 1000)

