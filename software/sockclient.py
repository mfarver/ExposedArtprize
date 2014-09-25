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
				'open_animations': [name for name, _ in anireg.anis(Animations.opening)],
				'close_animations': [name for name, _ in anireg.anis(Animations.opening)],
				'key': self._key
			})

	def power(self, func):
		self._power = func

	def animation(self, func):
		self._animation = func

	def stay_open(self, func):
		self._stay_open = func

	def on_power(self, data, _=None):
		print("on_power", data)
		if self._power:
			self._power(data)

	def on_animation(self, data, _=None):
		print("on_animation", data)
		if self._animation:
			self._animation(data)

	def on_stay_open(self, data, _=None):
		print("on_stay_open", data)
		if self.on_stay_open:
			self.on_stay_open(data)


	def run(self):
		with SocketIO('artprize.herokuapp.com') as self.sio:
			sio.on('power', self.on_power)
			sio.on('animation', self.on_animation)
			sio.on('stay_open', self.on_stay_open)
			sio.wait()