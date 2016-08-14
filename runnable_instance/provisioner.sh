#!/bin/bash

sudo rm /var/lib/mongodb/mongod.lock

sudo mongod --repair --dbpath /var/lib/mongodb

sudo mongod --fork --logpath /var/lib/mongodb/mongodb.log --dbpath /var/lib/mongodb 

sudo service mongod restart

sudo service zookeeper restart

sudo su vagrant

sudo nohup /home/vagrant/kafka/bin/kafka-server-start.sh /home/vagrant/kafka/config/server.properties > /home/vagrant/kafka/kafka.log 2>&1 &

