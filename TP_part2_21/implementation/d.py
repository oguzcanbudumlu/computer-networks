from socket import *		# socket library is imported for the communication
import threading			# threads are used for multi-homing functionality
import hashlib				# hashlib library is used when the data is cheksummed
import time 				# time library is used for timeouts 	
from datetime import datetime

TIMEOUT = 1.5					# timeout time in seconds for the socket, when no action in this give time, exception occurs
SOCKETBUFFERSIZE = 1024		# used to specify the size of the socket buffer
BROKERIP1 = "10.10.3.2"		# the ip address of the broker from which the file chunks will come
BROKERIP2 = "10.10.5.2"		# the ip address of the broker from which the file chunks will come

PORT1 = 20000				# the port number with which the first thread's socket will be binded
PORT2 = 30000				# the port number with which the second thread's socket will be binded
FILENAME = "output.txt" 	# the name of the file to which the data will be written
	
global outputStorage		# a global dictionary, threads will fill this with the coming chunks 
outputStorage = {}			# we use dictionary because key-value pair is very beneficial to order the received data with index number

def ReceivePacket(threadId, broker, port): 				# this function is used by the threads to receive coming pockets and fill the global dictionary
	destinationSocket = socket(AF_INET, SOCK_DGRAM)		# a socket is created to catch packets
	destinationSocket.bind((broker, port))				# the socket will be binded with port and listenig to the packets coming from the broker
	destinationSocket.settimeout(TIMEOUT)				# timeout is used to set a time out for the socket while waiting to receive packets
    
	print "The thread", threadId, "is ready to receive packets.."

	finished = False			# while the fin packet is not received, false
	brokerAddress = (broker, port)
	expectedSequenceNo = 1		# expected sequence number of the packet 

	while True:					# while fin packet has not come
		try:					# the packets are received below
			receivedPacket, brokerAddress = destinationSocket.recvfrom(SOCKETBUFFERSIZE)	# used to receive the packets coming from the broker
			sequenceNumber, payload, checksum = receivedPacket.split("#")					# split the coming packet into seqNo payload and checksum
			confirmation = hashlib.md5(sequenceNumber + "#" + payload + '#').hexdigest()	# create a checksum to check with the received checksum
			if (confirmation == checksum):									# if the checksums are matched
				if (int(sequenceNumber) == expectedSequenceNo):				# if the sequence number is the expected
					print sequenceNumber
					if (payload == "FIN"):									# if the payload is fin 
						finished = True										# then finished is true and process is done
					else:													# else the payload is ordinary payload that carries a chunk of the file
						index, data = payload.split("-")					# this payload contains a index of the chunk, they are splitted here
						outputStorage[int(index)] = data					# key is index, and value is the data, will be used for ordering
					expectedSequenceNo += 1									# expectedSeqNo increased to catch the next data
					packet = str(expectedSequenceNo) + "#"					# prepare the ack of the packet that has come 
					checksum = hashlib.md5(packet).hexdigest()				# checksum the packet
					packet = packet + checksum 								# checksum is attached to the packet
					destinationSocket.sendto(packet, brokerAddress)			# the ack packet is sent to the broker
				
		except:					# exception occured, when timeout is exceeded
			packet = str(expectedSequenceNo) + "#"					# prepare the ack of the packet that has come 
			checksum = hashlib.md5(packet).hexdigest()				# checksum the packet
			packet = packet + checksum 								# checksum is attached to the packet
			destinationSocket.sendto(packet, brokerAddress)			# the ack packet is sent to the broker
			if finished:		# if the fin packet received
				break			# then, finish the process

if __name__ == "__main__":
	# because the protocol will be multi-homing, we use two threads, each thread catches the half of payload chunks
	thread1 = threading.Thread(target = ReceivePacket, args = (1, BROKERIP1, PORT1))
	thread2 = threading.Thread(target = ReceivePacket, args = (2, BROKERIP2, PORT2))

	# threads are started to execute SendPacket function
	thread1.start()
	thread2.start()

	# after the execution, threads are joined with the main branch
	thread1.join()
	thread2.join()
	localTime = datetime.utcnow().strftime('%H:%M:%S:%f')
	output = open(FILENAME, "wb")			# open a file to merge the caught data chunks
	for i in range(0, len(outputStorage)):		# outputStorage is filled with the data chunks, from 0 to len
		output.write(outputStorage[i])			# write each data chunk into the file
	output.close()								# close the file
	print localTime
	
