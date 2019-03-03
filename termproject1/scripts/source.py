"""
------------------------------------
Group: 21
---------
2098820
Oguzcan Budumlu
---------
2257541
Omer Cetin
------------------------------------
 
This script connects source to broker using TCP.

"""

from socket import *
from datetime import datetime

import time
import ntplib

from time import ctime

c = ntplib.NTPClient()

brokerName = '10.10.1.2'
brokerPort = 12000
clientSocket = socket(AF_INET, SOCK_STREAM)  # create socket. AF_INET for IPv4 Internet protocols, SOCK_STREAM for TCP
clientSocket.connect((brokerName,brokerPort)) # connect to server, which is broker
packetCount = 1 # send 50 timestamps targeting destination to obtain sample data
for i in range (0, packetCount):
        #response = c.request('time1.google.com', version=3) # send request to obtain the clock in Google Server
        #localTime = datetime.fromtimestamp(response.orig_time)# convert response from Google server to datetime format
        #localTimeAsString = datetime.strftime(localTime, '%Y-%m-%d %H:%M:%S.%f') # convert to string format to send to broker
        clientSocket.send('test') # send timestamp to broker
        time.sleep(1) # prevent too much request in very short time to Google server

clientSocket.close()


