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
 
This script takes packets from routers
using UDP and after a time-out it prints
as a list.

"""


from thread import *
import threading 

from socket import *
from datetime import datetime

import time
import ntplib

isFinished = False
packetLists = [[],[]] # to hold difference between timestamps seperately coming from routers





def printBiggerList():
    """
    In packetLists[0] and packetLists[1], time differences between source and
    destination are hold for router 1 and router 2 respectively.
    Since UDP is used between broker and destination, packet loss may exist so
    route where minimum packet lost exists is evaluated.

    """
    if len(packetLists[0]) > len(packetLists[1]):
        print(packetLists[0])
    else:
        print(packetLists[1])


def appendToList(listNumber, timeDiff):
    """
    Adds sample (time difference) to related list.
    """    
    if listNumber == 1:
        packetLists[0].append(timeDiff)
    else:
        packetLists[1].append(timeDiff)


def threaded(portNumber, threadID): 
    """
    For each connection with a router, this function is called.
    
    """        
    c = ntplib.NTPClient()
    print("--------------")
    print(threadID)
    serverPort = portNumber
    serverSocket = socket(AF_INET, SOCK_DGRAM) # create socket. AF_INET for IPv4 Internet protocols, SOCK_DGRAM for UDP
    serverSocket.bind(('', serverPort)) # associate port number with this socket
    print("The server is ready to receive")
    while True:
        if isFinished == True:
                break
        message, clientAddress = serverSocket.recvfrom(26) # take source timestamp from router
        remoteTime = datetime.strptime(message, '%Y-%m-%d %H:%M:%S.%f') # convert timestamp to datetime format
        response = c.request('time1.google.com', version=3) # send request to obtain the clock in Google Server
        localTime = datetime.fromtimestamp(response.orig_time) # convert response from Google server to datetime format
        timeDiff = localTime - remoteTime # difference between source and destination time
        timeDiffAsMs = timeDiff.microseconds / 1000.0 + timeDiff.seconds * 1000.0 + timeDiff.days * 86400000.0 # difference in terms of milliseconds
        appendToList(threadID, timeDiffAsMs) # append to related packetList




def Main():
    """
    Here, threads are created for routers.(2 threads are for 2  routers.)
    In packetLists, time differences between source clock and destination
    clock are hold. 
    In order to understand whether packet receiving from routers continues, 
    it is checked that whether length of packet lists is increasing or not.
    If packet receiving is stopped for 3 seconds (referred as sleep time below), 
    it is assumed that receiving is finished.
    In the beginning, 30 seconds sleep is for establishing connection in the
    topology.

    """
    datetime.strptime('', '') # added due to a bug, reference: https://bugs.python.org/issue7980
    start_new_thread(threaded, (12003, 1)) # thread created
    start_new_thread(threaded, (12004, 2))
    time.sleep(30) 
    while True:
        prevSizeOfList = [len(packetLists[0]), len(packetLists[1])]
        time.sleep(3)
        currSizeOfList = [len(packetLists[0]), len(packetLists[1])]
        if prevSizeOfList == currSizeOfList: # understood that packet does not come any more
            global isFinished # finish loops in threads 
            isFinished = True
            printBiggerList()
            break




if __name__ == '__main__':
    Main() 

