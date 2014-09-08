#!/usr/bin/python3
"""
Coordinates motion with animations
"""
import http.server
import enum # PyPI's enum34 if not on 3.4
import socket
import threading
import time
from animations import Animations

class ServoStatus(enum.Enum):
	dunno = 0
	opening = 1
	opened = 2
	closing = 3
	closed = 4

class _ServoControl:
	"""
	Talks to the servo controller
	"""
	# Hey, Rich! Can you fill this in?
	enable = True
	def enable(self):
		self.enabled = True

	def disable(self):
		self.go_close()
		self.enabled = False

	def status(self) -> ServoStatus:
		# TODO
		return ServoStatus.dunno

	def position(self):
		# TODO
		return 0

	def go_open(self):
		if self.enabled:
			# TODO
			pass

	def go_close(self):
		if self.enabled:
			# TODO
			pass

ServoControl = _ServoControl()

class _AnimationControl:
	"""
	Talks to the network and changes the animation
	"""
	MYPORT = 0xEA00

	def __init__(self):
		self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

	def __call__(self, ani: Animations, **kw):
		if len(kw):
			raise NotImplementedError
		self._sock.sendto("{}\n".format(ani.value).encode("utf-8"), ('<broadcast>', self.MYPORT))

AnimationControl = _AnimationControl()

class ExposedHandler(http.server.BaseHTTPRequestHandler):
	"""
	This is to expose the motor controller to some kind of app server for internet-based interaction.

	NOTE: The app server must aggregate, cache, and throttle. This is not designed for more than a handful of clients.
	"""
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
		# TODO: Use Precondition Failed if commanded to open/close and it's currently disabled
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
	def run(cls, server_class=http.server.HTTPServer):
		"""
		Run the HTTP API server
		"""
		server_address = ('', 8000)
		httpd = server_class(server_address, cls)
		httpd.serve_forever()

def animation_controller():
	"""
	Thread for converting motor state to animations, and then broadcasting it out.
	"""
	# Default animation
	AnimationControl(Animations.idle)
	try:
		while True:
			s = ServoControl.status()
			# Some kind of logic to turn states into animations
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
			time.sleep(0) # Yield GIL
	finally:
		# Oops, going away now. Shut things down.
		AnimationControl(Animations.off)

if __name__ == '__main__':
	server = threading.Thread(target = ExposedHandler.run, name="httpd", daemon=True)
	server.start()
	animation_controller()