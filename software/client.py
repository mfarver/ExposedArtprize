#!/usr/bin/python3
"""
Client that actually sends frames to LED strip
"""
import array
import queue
import threading
from animations import AniReg
from sockclient import SocketClient

MAX_VALUE = 255
LED_COUNT = 1000*3

class AnimationRunner:
	default = None

	def __init__(self, slices):
		self.slices = [
			(sli, serial.Serial(fn))
			for sli, fn in slices
		]

	def spewframe(self, frame):
		"""
		Send a frame out to clients
		"""
		for sli,dev in self.slices:
			dev.setRTS(True)
			# TODO: do some frame flips if step < 0
			dev.write(frame[sli])
			dev.setRTS(False)

	def __iter__(self):
		frame = bytearray([0] * LED_COUNT)
		current = AniReg.random(None)
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
					if a in AniReg:
						a = AniReg[a]
					else:
						print("Unknown animation: {}".format(a))
						a = AniReg.random(None)
					kw = kw or {}
					current.close()
					current = a(frame, **kw)
					old_akw = akw
			try:
				frame = next(current)
			except StopIteration:
				current = AniReg.random(None)(frame)
				frame = next(current)
			self.spewframe(frame)

def parseArg(args=None):
	if args is None:
		args = sys.argv
	for arg in args:
		dev, sli = arg.split('=', 1)
		yield dev, slice(*(int(i) if i else None for i in sli.split(':')))

def main():
	q = queue.Queue()

	sc = SocketClient(q)

	client = threading.Thread(target=sc.run, name="netclient", daemon=True)
	client.start()

	ar = AnimationRunner(list(parseArg())) # FIXME: pass options to define how to talk to LEDs
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