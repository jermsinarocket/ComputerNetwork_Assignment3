#!/usr/bin/env python3
import socket
import sys
from threading import Thread
if sys.platform != 'win32': #SIGPIPE does not work for windows
  from signal import signal, SIGPIPE, SIG_DFL
  signal(SIGPIPE,SIG_DFL) #ignore broken pipe

# For handling client's connection to TEXT PORT, assign a thread to handle each client connection
def accept_text():
	"""
    Accept clients' connection to TEXT port.
	"""
	while True:
		client, client_address = SERVER_TEXT.accept()
		print("%s:%s has connected to the Server" % client_address)
		client.send(bytes("Enter your name: ", "utf8"))
		addresses_text[client] = client_address
		Thread(target=handle_client_text, args=(client,)).start()


# For handling client's connection to VOICE PORT, assign a thread tio handle each client connection
def accept_voice():
	"""
    Accept clients' connection to VOICE port.
	"""
	while True:
		client, client_address = SERVER_VOICE.accept()
		addresses_voice[client] = client_address
		Thread(target=handle_client_voice, args=(client,)).start()
		print("Voice has been enabled" )

def handle_client_text(client):
	"""
    Handles a message from the given socket.
    """
	# Receive Message
	name = client.recv(BUFSIZ).decode("utf8")
	welcome = 'Welcome %s! Type {quit} to exit the chat room.' % name
	client.send(bytes(welcome, "utf8"))
	msg = "%s has entered the chat room!" % name
	broadcast(bytes(msg, "utf8"))
	clients_text[client] = name

	while True:
		msg = client.recv(BUFSIZ)
		if msg != bytes("{quit}", "utf8"):
			#Append name to front of message
			broadcast(msg, name + ">> ")
		else:
			client.send(bytes("{quit}", "utf8"))
			client.close()
			erase_client(client)
			broadcast(bytes("%s has left the chat room." % name, "utf8"))
			break


def handle_client_voice(client):
	"""
	Handles Voice from the given socket.
 	"""
	# Receive Voice
	clients_voice[client] = 1

	while client in clients_voice:
		try:
			data = client.recv(BUFSIZ)
			broadcast(data, dtype='voice')
		except Exception as _:
			client.close()
			del clients_voice[client]


# Delete a text socket from client list
def erase_client(client):
	"""
    Removes Socket from Client List.
	"""
	del clients_text[client]
	del addresses_text[client]


# Broadcast a message to every client, depends on whether it is voice or text
def broadcast(msg, prefix="", dtype='text',):
	"""
    Broadcast message to clients, depending on data type.
	"""
	# Check if data is voice or text
	if dtype == 'text':
		for sock in clients_text:
			sock.send(bytes(prefix, "utf8") + msg)
	else:
		for sock in clients_voice:
			sock.send(msg)


clients_text = {}
addresses_text = {}
clients_voice = {}
addresses_voice = {}

HOST = '' # current machine's hostname - 127.0.0.1  (Change Accordingly)
PORT_TEXT = 2222 # Text Port of Server
PORT_VOICE = 55555 # Voice Port of Server
BUFSIZ = 1024 # buffer size for messages and Voices
ADDR_TEXT = (HOST, PORT_TEXT) # Bindings for text socket
ADDR_VOICE = (HOST, PORT_VOICE) # Bindings for voice sockfet


"""
Initiates the chat server.
"""
# establish server socket to listen on the given port
SERVER_TEXT = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
SERVER_TEXT.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
SERVER_TEXT.bind(ADDR_TEXT)

SERVER_VOICE = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
SERVER_VOICE.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
SERVER_VOICE.bind(ADDR_VOICE)

if __name__ == "__main__":
	SERVER_TEXT.listen(5)
	SERVER_VOICE.listen(5)
	print("Waiting for connection...")

	#Start accepting connection to Text Port
	ACCEPT_THREAD_TEXT = Thread(target=accept_text)
	ACCEPT_THREAD_TEXT.start()

	#Start accepting connection to Voice Port
	ACCEPT_THREAD_VOICE = Thread(target=accept_voice)
	ACCEPT_THREAD_VOICE.start()
    #Join the voice and text threads with the main thread
    #allow main thread to stop exectuing until execution of voice and text threads are coomplete
	ACCEPT_THREAD_VOICE.join()
	ACCEPT_THREAD_TEXT.join()
    #Close the server sockets
	SERVER_TEXT.close()
	SERVER_VOICE.close()
