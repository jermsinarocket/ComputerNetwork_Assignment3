#!/usr/bin/env python3

import socket
from threading import Thread
import pyaudio
from ctypes import *

# Audio quality
CHUNK = 8192
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
WIDTH = 2
ERROR_HANDLER_FUNC = CFUNCTYPE(None, c_char_p, c_int, c_char_p, c_int, c_char_p)

# Prevents the ALSA debug information from spamming stdout
def py_error_handler(filename, line, function, err, fmt):
	pass


# PyAudio configurations
c_error_handler = ERROR_HANDLER_FUNC(py_error_handler)
asound = cdll.LoadLibrary('libasound.so.2')
asound.snd_lib_error_set_handler(c_error_handler)

p = pyaudio.PyAudio()

#For sending stream over to the server
stream_send = p.open(
	format=pyaudio.paInt16,
	channels=CHANNELS,
	rate=RATE,
	input=True,
	frames_per_buffer=CHUNK)

#For receving stream from the server and playing the stream
stream_recv = p.open(
	format=p.get_format_from_width(WIDTH),
	channels=CHANNELS,
	rate=RATE,
	output=True,
	frames_per_buffer=CHUNK)


# For Receiving Text
def receive_text():
	while True:
		try:
			msg = client_socket_text.recv(BUFSIZ).decode("utf8")
			print(msg)
		except OSError:
			break


# For Receiving Voice
def receive_voice():
	while True:
		try:
			data = client_socket_voice.recv(BUFSIZ)
			stream_recv.write(data)
		except OSError:
			break


# Send Text to the Server
def send_text():
	while True:
		msg = input()
		print('\033[A\033[A')
		client_socket_text.send(bytes(msg, "utf8"))
		if msg == "{quit}":
			client_socket_text.close()
			client_socket_voice.close()
			quit()


# Send voice to the server
def send_voice():
	while True:
		try:
			data = stream_send.read(CHUNK)
			client_socket_voice.sendall(data)
		except OSError:
			break


HOST = input("Enter the Host: ") # Default 127.0.0.1
PORT_TEXT = 2222   # TEXT port of server to connect to
PORT_VOICE = 55555 # VOICE port of server to connect to

BUFSIZ = 1024
ADDR_TEXT = (HOST, PORT_TEXT)
ADDR_VOICE = (HOST, PORT_VOICE)

"""
Attempts to connect to the server Text Port
"""
client_socket_text = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket_text.connect(ADDR_TEXT)

"""
Attempts to connect to the server Voice Port
"""

client_socket_voice = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket_voice.connect(ADDR_VOICE)

receive_text_thread = Thread(target=receive_text)
receive_text_thread.start()

send_text_thread = Thread(target=send_text)
send_text_thread.start()

receive_voice_thread = Thread(target=receive_voice)
receive_voice_thread.start()

#Keep sending voice
send_voice()
