#!/usr/bin/python3
"""
Runs the server and the client in a single process
"""
import server
import client
import threading

if __name__ == '__main__':
	srv = threading.Thread(target=server.ExposedHandler.run, name="httpd", daemon=True)
	srv.start()
	ar = client.AnimationRunner([]) # FIXME: pass options to define how to talk to LEDs
	ari = iter(ar)
	next(ari)
	server.animation_controller(ari.send)