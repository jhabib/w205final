# Running the Code
The **runnable_instance** folder contains a Vagrantfile that will setup a VM with all components developed specifically for this project. The vagrant image won't have the SauronConsole and RLT. More about that later.

To run the code, please do the following:
- Clone this repository
- `cd` to `runnable_instance` folder
- from the `runnable_instance` folder, execute `vagrant up` from a command prompt or terminal

This should bring up a vagrant instance with MongoDB, Kafka, Python etc.

## Start a Kafka Producer:
- `vagrant ssh' into the vm
- `cd /data/w205final/sauron_data_pipeline/`
- `python sauron_producer.py`
Doing this will kick up a thread that will continuously poll the local MongoDB for new messages under sauron database (events and profiles) collections.
This producer keeps track of the last message sent to Kafka from profiles and events collections by adding the last sent _id to a MongoDB database called "counters". Within the "counters" database are "event_counters" and "profile_counters" collections for event and profile message _ids.

## Start the BigQuery handler for Profiles:
- `vagrant ssh` from a new termial
- `cd /data/w205final/sauron_data_pipeline/`
- `python start_profiles_bigquery_handler.py`
This will start consuming messages from the `profiles` Kafka topic and send them to the `profiles` table in sauron BigQuery database.

## Start the BigQuery handler for Events:
- `vagrant ssh` from a new termial
- `cd /data/w205final/sauron_data_pipeline/`
- `python start_events_bigquery_handler.py`
This will start consuming messages from the `events` Kafka topic and send them to the 'events' table in sauron BigQuery database.

## Notes on Running the Code
Make sure that ports 27017, 2181 and 9092 are free on your host machine. Vagrant will forward these to the vm. Or you can comment out these lines from the Vagrantfile if you don't want to forward these ports. Doing that will prevent SauronConsole from being able to access the MongoDB on the Vagrant vm. This is because SauronConsole is hard-coded to look for a MongoDB instance at `localhost:27017`.

## Resetting the Streaming
The MongoDB `sauron` database has about 350,000 documents for `events` and 600 or so for `profiles`. Most of these have been sent to BigQuery already and running the producers/handlers will exhaust the documents list pretty quickly. This is because the sauron_producer keeps track of the last _id it sent to Kafka and resumes sending from the next _id. Without RLT and SauronConsole running, new data will not be getting inserted into the MongoDB either.

To reset the streaming from scratch do the following:

- Delete the `event_counters` and `profile_counters` collections from the `counters` **database** in MongoDB, AND 
- Either, delete the `profiles` and `events` Tables on BigQuery and recreate them with the same name and schema; 
OR
- Create new tables in BigQuery for profiles and events (profiles_new, events_new) AND change the corresponding names in config.json

These steps should reset the streaming and allow you to stream data into BigQuery starting at _id==1 for `profiles` and `events`.
Please do not delete any collections under the `sauron` MongoDB database as that contains the source documents (messages) that will be sent to BigQuery. If you deleted the sauron database, you can always `vagrant destroy` and `vagrant up` again.


