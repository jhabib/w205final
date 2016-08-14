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

