#!/usr/bin/python3

import http.server
import enum
import socket
import threading
import time

class ServoStatus(enum.Enum):
	dunno = 0
	opening = 1
	opened = 2
	closing = 3
	closed = 4

class Animations(enum.Enum):
	opening = "opening"
	closing = "closing"
	opened = "opened"
	closed = "closed"
	idle = "idle"
	off = "off"

class _ServoControl:
	enable = True
	def enable(self):
		self.enabled = True

	def disable(self):
		self.go_close()
		self.enabled = False

	def status(self):
		return ServoControl.dunno

	def position(self):
		return 0

	def go_open(self):
		if self.enabled:
			pass

	def go_close(self):
		if self.enabled:
			pass

ServoControl = _ServoControl()

class _AnimationControl:
	MYPORT = 0xEA00

	def __init__(self):
		self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

	def __call__(self, ani):
		cs.sendto(ani.value+'\n', ('<broadcast>', MYPORT))

AnimationControl = _AnimationControl()

class ExposedHandler(http.server.BaseHTTPRequestHandler):
	def send_full_response(self, status, content=None):
		self.send_response(status)
		self.send_header('Content-Type', 'text/plain')
		self.send_header('Content-Length', len(content))
		self.end_headers()
		if content is not None:
			return content

	def do_GET(self):
		return self.send_full_response(200, "{} {} {}".format(ServoControl.status().name, ServoControl.position(), ServoControl.enabled))

	def do_POST(self):
		if self.path == '/open':
			ServoControl.go_open()
		elif self.path == '/close':
			ServoControl.go_close()
		elif self.path == '/enable':
			ServoControl.enable()
		elif self.path == '/disable':
			ServoControl.disable()
		else:
			return self.send_full_response(404)
		return self.send_full_response(200, "ok")

	@classmethod
	def run(cls, server_class=http.serverHTTPServer):
		server_address = ('', 8000)
		httpd = server_class(server_address, cls)
		httpd.serve_forever()

def animation_controller():
	AnimationControl(Animations.idle)
	try:
		while True:
			s = ServoControl.status()
			if s == ServoStatus.opening:
				AnimationControl(Animations.opening)
			elif s == ServoStatus.opened:
				AnimationControl(Animations.opened)
			elif s == ServoStatus.closing:
				AnimationControl(Animations.closing)
			elif s == ServoStatus.closed:
				AnimationControl(Animations.closed)
				# TODO: Time out back to idle
			else:
				AnimationControl(Animations.idle)
			time.sleep(0)
	finally:
		AnimationControl(Animations.off)