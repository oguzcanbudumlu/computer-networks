import sys

from socket import *		# socket library is imported for the communication
import threading			# threads are used for multi-homing functionality
import hashlib				# hashlib library is used when the data is cheksummed
import time 				# time library is used for timeouts 			
	
FILENAME = "temp.txt" 		# the file name of the file which is received from the source and sent to the destination
PAYLOADSIZE = 512			# this is the payload size of a packet, the pure size of the data apart from the index no, checksum vs.
SOCKETBUFFERSIZE = 1024		# used to specify the size of the socket buffer
TIMEOUT = 1 				# timeout time in seconds for the socket, when no action in this give time, exception occurs
DESTINATION1 = "10.10.3.2"		# the first ip address of the destination device 
DESTINATION2 = "10.10.5.2"		# the second ip address of the destination device
PORT1 = 20000			# the port number of the destination through which the first thread will run
PORT2 = 30000			# the port number of the destination through which the second thread will run
TCPPORT = 10000			# the port number for the tcp communication in which the input file comes from the source
MULTIHOMINGCOUNT = 2 			# count of multihoming 
tcpSocket = socket(AF_INET, SOCK_STREAM)	# the socket used to get the input file from the source
tcpSocket.bind(("", TCPPORT))		# the socket is binded with the port, any device can connect to this port
tcpSocket.listen(1)			# at a time, only one device is allowed to connect, simply the socket listens to one device

print "The broker is waiting for the file that will come from the source.."

connection, address = tcpSocket.accept()	# the connection request coming from the source (address) is accepted 
with open(FILENAME, 'wb') as file:			# the file is opened for writing the piece of the file coming from the source
    while True:								# while true 
        data = connection.recv(SOCKETBUFFERSIZE)		# data is received from the connection established with the source
        if not data:						# if the data is null, 
            break							# then break
        file.write(data)					# the data coming from the source is written to the file 

file.close()				# the file is closed after the delivery of the file
connection.close()			# the connection with the source is closed after the delivery

payloadChunks = []			# the file will be divided into the chunks, the chunks will be stored in this list

file = open(FILENAME, "rb")					# the file received from the source is now opened for reading 
payload = file.read(PAYLOADSIZE)			# the file will be divided into the chuncks with size PAYLOADSIZE
index = 0									# index is used for indexing all the chunks, later will be used for ordering the data in the destination
while (payload):							# while the payload is not null
	payload = str(index) + "-" + payload 	# index number is attached to the payload
	payloadChunks.append(payload)			# the indexed payload is appended into the list
	payload = file.read(PAYLOADSIZE)		# the next payload is readed
	index = index + 1						# index incremented
file.close()		# the file is closed after the division

divider = len(payloadChunks) / MULTIHOMINGCOUNT		# this variable is used to divide the payload in half for multi-homing

payloadChunks1 = [""]			# the first half of the payload list that will be sent using the thread 1
payloadChunks2 = [""]			# the second half of the payload list that will be sent using the thread 2

for i in range(0, divider):						# the first half of the list
	payloadChunks1.append(payloadChunks[i])		# appended to the first payload chunk list

for j in range(divider, len(payloadChunks)):	# the second half of the list
	payloadChunks2.append(payloadChunks[j])		# appended to the second payload chunk list

def CreatePacket(sequenceNumber, payload):					# this function is used to create packets which will be sent 
	packet = str(sequenceNumber) + "#" + payload + "#"		# sequence number and the payload are combined adding "#" in between
	checksum = hashlib.md5(packet).hexdigest()				# the combination is hashed and stored in checksum
	packet = packet + checksum								# checksum is combined to the combination
	return packet 											# return the combination created

def SendPacket(destination, port, chunks):		# this function is used by the threads to transmit the data chunks 	
	brokerSocket = socket(AF_INET, SOCK_DGRAM) 		# the UDP socket is created by which the data will be sent
	brokerSocket.settimeout(TIMEOUT)               	# the timeout TIMEOUT is set for the socket when waiting for receiving a data from the destination

	sequenceNumber = 1			# the chunks will be sent in order based on the sequenceNumber
	windowBase = 1				# the window base, it will be incremented when expected ack comes
	windowSize = 1000   			# this is the window size, used to buffer unacked packets
	window = []					# used to store unacked packets
	done = False     			# while go back n process is not done its false, becomes true when all the packets sent 

	chunksCount = len(chunks)		# the number of packets to be sent

	while not done or window:			# while there are still unacked packets or all the packets are not sent
		if (sequenceNumber < windowBase + windowSize) and not done:		# the packets that has sequence number less than windowBase + windowSize can be sent and go back n not done
			payload = chunks[sequenceNumber]							# get the payload of the packet that will be sent
			packet = CreatePacket(sequenceNumber, payload)				# create the packet that will be sent, sequenceNo + payload + chekcsum( sequenceNo + payload )
			brokerSocket.sendto(packet, (destination, port))			# the created packet is sent here
			sequenceNumber += 1											# sequnceNumber incremented to send the next packet
			if (sequenceNumber == chunksCount):							# if all the packets are sent
				done = True 											# then the process is done, but there still can be packet in the window
			window.append(packet)										# the packet sent will be added to the window

		try:		# get the ack of the packets below
			receivedPacket, destAddress = brokerSocket.recvfrom(SOCKETBUFFERSIZE)	# wait for the ack, if there is no ack coming, timeout will occur
			ackNumber, checksum = receivedPacket.split("#")				# the ack packet is splitted here into ackNo and checksum
			confirmation = hashlib.md5(ackNumber + "#").hexdigest()		# a checksum is created here to compare with the received checksum
			if (confirmation == checksum):								# if the created checksum and the received cheksum matches
				print ackNumber
				while ((int(ackNumber) > windowBase) and window):		# while the window is not empty and if the acknumber is equal to the windowbase + 1
					del window[0]										# delete the first unacked packet from the window cuz it was just acked
					windowBase += 1										# window base is incremented meaning the window is slided 

		except:															# if the expected ack packet does not come in a give time(TIMEOUT), exception occurs
			for packet in window:										# all the packets in the window are re-sent 
				brokerSocket.sendto(packet, (destination, port))		# packets are re-sent

	while True:			# this is the last part to finish the session
		packet = CreatePacket(sequenceNumber, "FIN")					# a packet is created with a payload "FIN", sequenceNumber has no sense here but added to parse it correctly in the destination
		brokerSocket.sendto(packet, (destination, port))				# the fin packet is sent

		try:															# ack of the fin packet
			receivedPacket, destAddress = brokerSocket.recvfrom(SOCKETBUFFERSIZE)	# wait for the ack of the fin packet to receive
			ackNumber, checksum = receivedPacket.split("#")				# split the coming packet
			confirmation = hashlib.md5(ackNumber + "#").hexdigest()		# checksum is created to check if the data is not correpted along the way coming
			if (confirmation == checksum):								# if the checksums match
				break													# everthing is over the file is successfully sent 

		except:						# if the ack of the fin packet does not come, exception occurs because of the timeout
			continue				# send the packet again and wait for the ack again

if __name__ == "__main__":
	# because the protocol will be multi-homing, we use two threads, each thread sends the half of payload chunks
	thread1 = threading.Thread(target = SendPacket, args = (DESTINATION1, PORT1, payloadChunks1))
	thread2 = threading.Thread(target = SendPacket, args = (DESTINATION2, PORT2, payloadChunks2))

	# threads are started to execute SendPacket function
	thread1.start()
	thread2.start()

	# after the execution, threads are joined with the main branch
	thread1.join()
	thread2.join()
