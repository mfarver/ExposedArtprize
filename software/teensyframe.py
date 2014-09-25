import serial
class TeensyDisplay:
	def __init__(self, dev):
		self._dev = serial.Serial(dev)

	def blt(self, frame, flip=False):
		self._dev.setRTS(True)
		# TODO: do some frame flips if necessary
		self._dev.write(frame[sli])
		self._dev.setRTS(False)
