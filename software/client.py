#!/usr/bin/python3
"""
Client that actually sends frames to LED strip
"""
import array
import queue
import threading
import sys
from animations import AniReg, LED_COUNT
from sockclient import SocketClient
from teensyframe import TeensyDisplay

class AnimationRunner:
	default = None

	def __init__(self, slices):
		self.slices = [
			(sli, TeensyDisplay(fn))
			for sli, fn in slices
		]

	def spewframe(self, frame):
		"""
		Send a frame out to devices
		"""
		for sli,dev in self.slices:
			dev.blt(frame[sli], flip=(sli.step < 0 if sli.step else False))

	def __iter__(self):
		frame = bytearray([0] * LED_COUNT)
		current = AniReg.random(None)(frame)
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
						a = AniReg.random(None)(frame)
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
	"""
	Parses out arguments in the form of /dev/ttyACM0=1:3:5
	"""
	if args is None:
		args = sys.argv[1:]
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