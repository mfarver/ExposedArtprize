#!/usr/bin/python3
"""
Client that actually sends frames to LED strip
"""
import socket
import array
import time
import math
import queue
import threading
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

	def __init__(self, slices):
		self.slices = [
			(sli, open(fn, 'wb'))
			for sli, fn in slices
		]
		print(self.anireg)

	def spewframe(self, frame):
		"""
		Send a frame out to clients
		"""
		for sli,dev in self.slices:
			# TODO: Perform byte reversal if slice.step < 0
			dev.write("".join("{:02X}".format(b) for b in frame[sli]) + "\n")

	def __iter__(self):
		frame = array.array('B', [0] * LED_COUNT)
		current = type(self).default(frame)
		old_akw = None
		while True:
			akw = yield
			if akw is not None:
				if akw != old_akw:
					if isinstance(akw, tuple):
						a, kw = akw
					else:
						a, kw = akw, {}
					print("Change: {} {}".format(a, kw))
					if a in self.anireg:
						a = self.anireg[a]
					else:
						print("Unknown animation: {}".format(a))
						a = type(self).default
					kw = kw or {}
					current.close()
					current = a(frame, **kw)
					old_akw = akw
			try:
				frame = next(current)
			except StopIteration:
				current = type(self).default(frame)
				frame = next(current)
			self.spewframe(frame)


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
			frame[i] = round((math.sin(i / length * 2 * math.pi + cycle) + 1) * MAX_VALUE/2)
		yield frame


def main():
	q = queue.Queue()
	def datagrabber():
		data= AnimationClient.getone()
		try:
			q.put(data)
		except queue.Full:
			# Discard data
			pass

	client = threading.Thread(target=datagrabber, name="netclient", daemon=True)
	client.start()

	ar = AnimationRunner([]) # FIXME: pass options to define how to talk to LEDs
	ari = iter(ar)
	while True:
		try:
			a, kw = q.get_nowait()
		except queue.Empty:
			next(ari)
		else:
			ari.send(a, kw)
		
if __name__ == '__main__':
	main()