@echo off

@echo changing to kafka installation directory
cd C:\kafka_2.11-0.10.0.0

@echo starting zookeeper
.\bin\windows\zookeeper-server-start.bat .\config\zookeeper.properties



@echo starting kafka
cd C:\kafka_2.11-0.10.0.0
.\bin\windows\kafka-server-start.bat .\config\server.properties