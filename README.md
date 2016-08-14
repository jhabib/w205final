# Instructions
This document describes the various components in the project and provides instructions on how to run the various components.

## Project Components
This project consists of many different components one of which is proprietary (cannot be *fully* shared) and one of which is licensed from a third party (cannot be shared at all).

### Third Party Component (RLT)
In the Casinos, real Slot machines communicate with a host system using a messaging protocol called G2S. Real Slot machines are very expensive (~ $5,000 for a development rig) and time consuming to setup, so we use a 3rd party application to simulate gameplay data during development. This application is called RadBlue Load Tester (RLT). RLT generates G2S messages as if there were one or more slot machines communicating to the host. Unfortunately, RLT is licensed to my development workstation and the license key is bound to the Network card's MAC address and my email. Therefore, I cannot run RLT on any other machine. I also cannot request another license for RLT as that is quite expensive for the company.

So, in absence of RLT, I won't be able to show you G2S data coming in from a simulated slot machine to the G2S Host. We can come up with creative ways to make this happen if you can spawn up an instance of SauronConsole with a public IP somewhere.

### Proprietary Component (G2S Host)
G2S Host is what communicates with Slot machines in Casinos. At work, we have an implementation of G2S Host that we use in various production applications. For this project, the G2S Host was updated as follows:
- Convert G2S messages from XML to JSON
- Save the JSON messages into a MongoDB database

While I cannot share the *entire* sorce code of the G2S Host, I can share code snippets where I deal with data conversion from XML to JSON, and with storing data into MongoDB.  I can also share a .Net console app (DLLs and EXEs, not the whole source) that loads the various components of the G2S Host. This console app is called SauronConsole.

If you can run this console app on a Windows PC (Win 7, x64 or similar) and give it a public IP address, I can point RLT to it and show data streaming in. That PC must meet the following requirements:
- Have an IP address that I can access from the (public) Internet
- Have ports 9090 and 9091 open and accessible. RLT will need to connect to port 9090 for http and 9091 for https.
- Have a local instance of MongoDB running and accessible at port 27017
- Have .Net Framework 4.5.1

I have also recorded a video of this RLT/G2S-stream-to-MongoDB process that you can download at: 

### Components Developed Specifically for this Project
These are components that I developed specifically for the class project and have all the source code available. There is no restriction on the use of these components.

