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
 
This script takes packets from source using TCP and 
sends them to both router 1 and router 2 using UDP.

"""


from socket import *

brokerPort = 12000
brokerSocket = socket(AF_INET,SOCK_STREAM) # create socket for source. AF_INET for IPv4 Internet protocols, SOCK_STREAM for TCP
brokerSocket.bind(('', brokerPort)) # associate port number with this socket
brokerSocket.listen(1) # process in sleep mode waits for incoming connection (source connection),  parameter 1 for maximum connection number

routerName1 = '10.10.3.2'
routerPort1 = 12001

routerName2 = '10.10.5.2'
routerPort2 = 12002

print 'The server is ready to receive'

connectionSocket, addr = brokerSocket.accept() # acknowledge source connection
clientSocket1 = socket(AF_INET, SOCK_DGRAM) # create socket for router1. SOCK_DGRAM for UDP
clientSocket2 = socket(AF_INET, SOCK_DGRAM) # create socket for router2

packetCount = 1 # number of sent timestamp to obtain sample data

for i in range (0, packetCount):
        remoteTime = connectionSocket.recv(26) # take timestamp coming from source, 26 for length of timestamp
        clientSocket1.sendto(remoteTime, (routerName1, routerPort1)) # send timestamp to router 1
        clientSocket2.sendto(remoteTime, (routerName2, routerPort2)) # send timestamp data to router 2

connectionSocket.close()
clientSocket1.close()
clientSocket2.close()
