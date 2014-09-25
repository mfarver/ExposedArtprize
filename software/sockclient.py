from socketIO_client import SocketIO
import animations

class SocketClient:
	sio = None
	_power = None
	_animation = None
	_stay_open = None

	def __init__(self, key):
		self._key = key

	def state_change(self, state):
		if self.sio:
			self.sio.emit('state_change', {'state': state.name.upper()})

	def pi_config(self, anireg=None):
		if anireg is None:
			anireg = animations.AniReg
		if self.sio:
			self.sio.emit('pi_config', {
				'open_animations': [func.__name__ for func in anireg[Animations.opening]],
				'close_animations': [func.__name__ for func in anireg[Animations.closing]],
				'key': self._key
			})

	def power(self, func):
		self._power = func

	def animation(self, func):
		self._animation = func

	def stay_open(self, func):
		self._stay_open = func

	def on_power(self, data, _=None):
		if self._power:
			self._power(data)

	def on_animation(self, data, _=None):
		if self._animation:
			self._animation(data)

	def on_stay_open(self, data, _=None):
		if self.on_stay_open:
			self.on_stay_open(data)


	def run(self):
		with SocketIO('http://artprize.herokuapp.com/raspi', 8000) as self.sio:
			sio.on('power', self.on_power)
			sio.on('animation', self.on_animation)
			sio.on('stay_open', self.on_stay_open)
			sio.wait()