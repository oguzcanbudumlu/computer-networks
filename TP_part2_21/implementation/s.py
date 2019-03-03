from socket import *		# socket library imported for the communication
from datetime import datetime

FILENAME = "input.txt"		# filename is stored in a macro this will be the file to be transmitted
BROKER = "10.10.1.2"     	# broker's ip address
SOCKETBUFFERSIZE = 1024		# used to specify the size of the socket buffer
PORT = 10000				# specifies the broker's port throuhg which the file will be sent

sourceSocket = socket(AF_INET, SOCK_STREAM)		# socket that is used to transmit the file over TCP

sourceSocket.connect((BROKER, PORT))		# the socket is connected to the broker's port
localTime = datetime.utcnow().strftime('%H:%M:%S:%f')
print localTime
file = open(FILENAME,'rb')         	# the file to be sent is opened to send the data
data = file.read(1024)				# the file is sent piece by piece, this is the first piece
while (data):						# while data is not eof
    sourceSocket.send(data)			# the piece is sent to the broker here
    data = file.read(1024)			# data is the next available piece
file.close()						# after the sending process is done, file is closed

sourceSocket.close()		# after the data is sent, the socket is closed
print "sent"
