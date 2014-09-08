#!/usr/bin/python3
"""
Client that actually sends frames to LED strip
"""
import socket
from animations import Animations

class _AnimationControl:
	"""
	Talks to the network and changes the animation
	"""
	MYPORT = 0xEA00

	def __init__(self):
		self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

	def getone(self) -> (str, dict):
		data = self._sock.recv(4*1024)
		text = data.decode('utf-8')
		if text.endswith('\n'):
			text = text[:-1]
		return text, {}

