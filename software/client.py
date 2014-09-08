#!/usr/bin/python3
"""
Client that actually sends frames to LED strip
"""
import socket
import array
from animations import Animations

LED_COUNT = 500*3

class _AnimationClient:
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
		ani = Animations.__members__[text]
		return ani, {}

AnimationClient = _AnimationClient()

class AnimationRunner:
	anireg = {}
	default = None

	def __iter__(self):
		frame = array.array('B', '\0' * LED_COUNT)
		current = self.default(frame)
		while True:
			akw = yield
			if akw is not None:
				a,kw = akw
				kw = kw or {}
				current.close()
				current = a(frame, **kw)
			try:
				frame = next(current)
			except StopIteration:
				current = self.default(frame)
			# TODO: Send frame


def animation(ani: Animations, *, default=False):
	def _(func):
		AnimationRunner.anireg[ani] = func
		if default:
			AnimationRunner.default = func
		return func
	return _

@animation(Animations.off, default=True)
def ani_off(frame):
	for i in range(len(frame)):
		frame[i] = 0
	while True:
		yield frame


