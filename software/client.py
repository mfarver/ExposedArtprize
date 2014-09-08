#!/usr/bin/python3
"""
Client that actually sends frames to LED strip
"""
import socket
import array
import time
import math
from animations import Animations

MAX_VALUE = 255
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
				if a in self.anireg:
					a = self.anireg[a]
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

@animation(Animations.off)
def ani_off(frame):
	for i in range(len(frame)):
		frame[i] = 0
	while True:
		yield frame

@animation(Animations.idle, default=True)
def ani_sine(frame, *, length=50, freq=5.0):
	zero = time.time()
	multi = 2 * math.pi / freq
	while True:
		offset = time.time() - zero
		cycle = offset * multi
		for i in range(len(frame)):
			frame[i] = sin(i / length * 2 * math.pi + cycle) * MAX_VALUE
		yield frame


def main():
	ar = AnimationRunner() # FIXME: pass options to define how to talk to LEDs
	ari = iter(ar)
	while True:
		a, kw = AnimationClient.getone()
		ari.send(a, kw)
		# FIXME: call next(ari) regularly
