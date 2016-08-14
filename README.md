# Instructions
This document describes the various components in the project and provides instructions on how to run the various components.

# Project Components
This project consists of many different components one of which is proprietary (cannot be *fully* shared) and one of which is licensed from a third party (cannot be shared at all).

## Third Party Component (RLT)
In the Casinos, real Slot machines communicate with a host system using a messaging protocol called G2S. Real Slot machines are very expensive (~ $5,000 for a development rig) and time consuming to setup, so we use a 3rd party application to simulate gameplay data during development. This application is called RadBlue Load Tester (RLT). RLT generates G2S messages as if there were one or more slot machines communicating to the host. Unfortunately, RLT is licensed to my development workstation and the license key is bound to the Network card's MAC address and my email. Therefore, I cannot run RLT on any other machine. I also cannot request another license for RLT as that is quite expensive for the company.

So, in absence of RLT, I won't be able to show you G2S data coming in from a simulated slot machine to the G2S Host. We can come up with creative ways to make this happen if you can spawn up an instance of SauronConsole with a public IP somewhere.

## Proprietary Component (G2S Host)
G2S Host is what communicates with Slot machines in Casinos. At work, we have an implementation of G2S Host that we use in various production applications. For this project, the G2S Host was updated as follows:
- Convert G2S messages from XML to JSON
- Save the JSON messages into a MongoDB database

While I cannot share the *entire* sorce code of the G2S Host, I can share code snippets where I deal with data conversion from XML to JSON, and with storing data into MongoDB. Code snippers are available in the directory called **csharp_code_snippets**.

I can also share a compiled .Net console app that loads the various components of the G2S Host. This console app is called **SauronConsole**. If you can run SauronConsole on a Windows PC (Win 7, x64 or similar) and give it a public IP address, I can point RLT to it and show data streaming in. That PC must meet the following requirements:
- Have an IP address that I can access from the (public) Internet
- Have ports 9090 and 9091 open and accessible. RLT will need to connect to port 9090 for http and 9091 for https.
- Have a local instance of MongoDB running and accessible on port 27017 (no passwords please)
- Have .Net Framework 4.5.1

SauronConsole can be downloaded at this URL: 

I have also recorded a video of this RLT/G2S-stream-to-MongoDB process that you can download at: 

## Components Developed Specifically for this Project
These are components that I developed specifically for the class project and have all the source code available. There is no restriction on the use of these components.

Source code for these components is in **sauron_data_pipeline**.

### Project Configuration
**config.json** 

This file contains URLs and topic/table names for Kafka, BigQuery and MongoDB (counters collection). I will describe below how some of these can be changed to restart the streaming process from scratch.

```json
{
  "kafka": {
    "uri": "localhost:9092",
    "topics": {
      "profiles": "profiles",
      "events": "events"
    }
  },
  "bigquery": {
    "projectid": "sauronbigquery",
    "dataset": "sauron",
    "tables": {
      "profiles": "profiles",
      "events": "events"
    }
  },
  "local_mongodb": {
    "uri": "localhost:27017",
    "source_db": "sauron",
    "source_collections": {
      "profiles": "profile",
      "events": "event"
    },
    "counters_db": "counters",
    "counters_collection": {
      "profiles": "profile_counters",
      "events": "event_counters"
    }
  }
}
```

To reset streaming, create new tables in BigQuery for events and profiles and update the names in config.json e.g. `profiles_new` and `events_new`. AND, drop the `profile_counters` and `event_counters` collections from the `counters` database in MongoDB. This is described in more detail below.


### MongoDB Interaction
**mongo_collection_manager.py** 

This wraps the collection.find and collection.remove functions in pymongo's MongoClient. This is there more for convenience than anything else. For production, I will either strip this out or make it a more complete wrapper. Right now, this is only used in sauron_producer.py to get data from the source document collections i.e. the collections where the G2S Host dumps G2S messages that have come in from Slot machines (RLT). All other interaction with MongoDB e.g. updating the counter database, is still handled directly with MongoClient.

### Kafka Interaction
**sauron_producer.py** 

This implements a Kafka producer class, and creates two instances of the class when run. The producer has the following jobs:
- Get data from a MongoDB collection
- Send data to a Topic in a Kafka queue
- Save the _id of the last data item sent to Kafka (so we can resume where we left off)

When you run sauron_producer.py, it will create two threads: one for the "profiles" collection/topic and another for the "events" collection/topic. The threads keep running indefinitely and poll for new data from MongoDB.

**sauron_consumer.py**

This implements a SauronConsumer class, used for retrieving data from a Kafka topic. It essentially gets a bunch of messages from a Kafka topic and calls a "callback" function for each message. There is a test function implemented in sauron_consumer.py which will print messages to the console.

### Google BigQuery Interaction

**sauron_bigquery_manager.py**

This implements all the classes necessary for getting the data from a Kafka Consumer, batching up that data in memory, and inserting all the data in the batch to a bigquery table.

**start_events_bigquery_handler.py** and **start_profiles_bigquery_handler.py**

These are setup scripts to launch the bigquery handlers for the "profiles" and "events" data sources. The main job of the scripts is to get the Google API credentials from an environment variable, and pass the credentials and config file to the bigquery handler setup.

### Google BigQuery Project Structure
The BigQuery project is called "sauronbigquery" and has the following structure:

| Component | Name/Id |
| --------- | --------- |
| Project Id | sauronbigquery |
| Dataset Name | sauron | 
| Table | profiles - each Egm has "profiles" associated with it that contain identifiers, denominations, meters etc. Essentially, meta data about the various classes in G2S.
Table | events - Events are the actual messages that come in from Egms. | 
| View | egmWinLossOverTime - shows wagers and wins over time |
| View | view_winLossByEgm - shows aggregate wagers and wins | 
| View | wagerCategoryCountsByEgm - shows counts of various wager categories by Egm. This would show null for everything because we do not have wager categories in simulated Egms.

The "profiles" and "events" tables are pretty simple. The both have the same structure:

- _id (integer) - an ever incremening _id assigned to each message as it comes in 
- Topic (string) - defines whether an event or a profile came in; a little redundant at this point
- Key (string) - a string of the form "Unique_EgmId-G2SMessage_Code-eventId 
- Value (string) - a JSON encoded string representing the entire contents of a G2S message 

Please note that the tables in BigQuery are append-only and I have not yet implemented table partitioning or jobs to delete tables after some time. So the tables will continue to grow as new data comes in - up to the limit that Google allows.

### Tableau Workbook
I created a Tableau workbook called **sauron_charts** to help visualize some data. Our marketing folks use Tableau so I figured I'd create a few examples for them.

Note: our RLT load test scripts wager and win $100 per bet. Since that would result in atrocious aggregate values, I've used log values to make things look more realistic. I also multiplied the wins and wagers with a random number in the BigQuery view (egmWinLossOverTime) to make things a little more realistic.

Tableau worksheets:

- logWinsWagersPerHour - average of wagers and wins per hour per Egm. This should tell marketing how much money is bet and won on an Egm per hour.
- wagersWinsHistogram - wagers and wins binned into different dolalr values e.g. $0-$10, $11-$20 and so forth. This should tell marketing people what's the most popular wager amount.
- netPlayerWinPerHour - (wager - win) aggregated per hour per Egm. Pretty meaningless but marketing people like this kind of stuff.
- cumulativePlayerWinsOverTime - a lot like the last graph but shows cumulative (wager-win) over time

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


