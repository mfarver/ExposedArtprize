from socketIO_client import SocketIO
import animations

class SocketClient:
	sio = None
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
			})

	def on_animation(self, *args):
		pass

	def on_animation(self, *args):
		pass

	def on_stay_open(self, *args):
		pass


	def run(self):
		with SocketIO('http://artprize.herokuapp.com/raspi', 8000) as self.sio:
			sio.on('power', self.on_power)
			sio.on('animation', self.on_animation)
			sio.on('stay_open', self.on_stay_open)
			sio.wait()