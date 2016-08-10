from sauron_bigquery_manager import *
from multiprocessing import Queue
from oauth2client.client import GoogleCredentials

if __name__ == '__main__':
    with open('config.json') as config_file:
        config = json.load(config_file)

    profiles_shared_queue = Queue()
    profiles_topic = 'profiles'
    profiles_table = 'profiles'

    # GOOGLE_APPLICATION_CREDENTIALS environment variable must be set
    # And it must point to the service account key (.json)
    credentials = GoogleCredentials.get_application_default()

    print('setting up bigquery handler for %s' % (profiles_topic))
    handler_setup(profiles_topic, profiles_table, profiles_shared_queue, config, credentials, 5, 50)

