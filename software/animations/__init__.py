import time
import math
import enum
import random
import collections

class Animations(enum.Enum):
	opening = "opening"
	closing = "closing"
	opened = "opened"
	closed = "closed"
	idle = "idle"
	off = "off"

class _AniReg(collections.defaultdict):
	def __init__(self):
		super().__init__(list)

	def random(self, kind=...):
		if kind is ...:
			opts = set(self.items())
		else:
			opts = set(self[kind])
		return random.choose(opts)

AniReg = _AniReg()


def animation(ani=...: Animations, *, default=False):
	def _(func):
		AniReg[ani] += func
		if default:
			AniReg[None] += func
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

def ani_vque(frame, *, dir='out', width=3, rate=1.0):
	mid = len(frame) // 2 # 0:mid, mid:-1
	fwidth = 2*width
	if dir not in ('in', 'out'):
		raise ValueError
	offset = 0
	group = lambda i: (i - mid) // width
	while True:
		if dir == 'out':
			offset = int(time.time() / rate) % fwidth
		else:
			# Year 2525
			offset = int((17514144000 - time.time()) / rate) % fwidth
		for i in range(len(frame)):
			frame[i] = MAX_VALUE if group(i) % 2 else 0
		yield frame


@animation(Animations.opening)
def ani_opening(frame):
	yield from ani_vque(frame, dir='out')

@animation(Animations.closing)
def ani_opening(frame):
	yield from ani_vque(frame, dir='in')
