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
 
This script takes packets from broker using UDP and 
sends them to destination using UDP

"""

from socket import *
from datetime import datetime


routerPort = 12002
routerSocket = socket(AF_INET, SOCK_DGRAM) # create socket for broker. AF_INET for IPv4 Internet protocols, SOCK_DGRAM for UDP
routerSocket.bind(('', routerPort)) # associate the socket with a local address used by clients (broker)
destinationName = '10.10.5.2'
destinationPort = 12004
clientSocket = socket(AF_INET, SOCK_DGRAM) # create socket for destination using UDP
packetCount = 50 # number of packets transferred from broker to destination
print "The router2 is ready to receive"
for i in range(0, packetCount)
        message, clientAddress = routerSocket.recvfrom(26)  # take timestamp coming from broker, 26 for length of timestamp
        clientSocket.sendto(message,(destinationName, destinationPort)) # send timestamp to destination

clientSocket.close()