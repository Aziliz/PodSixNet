import socket
import sys

from async import poll, asyncore
from Channel import Channel

class Server(asyncore.dispatcher):
	channelClass = Channel
	
	def __init__(self, channelClass=None, localaddr=("127.0.0.1", 31425), listeners=5):
		if channelClass:
			self.channelClass = channelClass
		self._map = {}
		self.channels = []
		asyncore.dispatcher.__init__(self, map=self._map)
		self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
		self.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
		self.set_reuse_addr()
		self.bind(localaddr)
		self.listen(listeners)
	
	def handle_accept(self):
		try:
			conn, addr = self.accept()
		except socket.error:
			print 'warning: server accept() threw an exception'
			return
		except TypeError:
			print 'warning: server accept() threw EWOULDBLOCK'
			return
		
		self.channels.append(self.channelClass(conn, addr, self, self._map))
		self.channels[-1].Send({"action": "connected"})
		if hasattr(self, "Connected"):
			self.Connected(self.channels[-1], addr)
	
	def Pump(self):
		[c.Pump() for c in self.channels]
		poll(map=self._map)

#########################
#	Test stub	#
#########################

if __name__ == "__main__":
	class ServerChannel(Channel):
		def Network_hello(self, data):
			print "*Server* ran test method for 'hello' action"
			print "*Server* received:", data
	
	class EndPointChannel(Channel):
		def Connected(self):
			print "*EndPoint* Connected()"
		
		def Network_connected(self, data):
			print "*EndPoint* Network_connected(", data, ")"
			print "*EndPoint* initiating send"
			outgoing.Send({"action": "hello", "data": {"a": 321, "b": [2, 3, 4], "c": ["afw", "wafF", "aa", "weEEW", "w234r"], "d": ["x"] * 256}})
	
	def Connected(channel, addr):
		print "*Server* Connected() ", channel, "connected on", addr
	
	server = Server(channelClass=ServerChannel)
	server.Connected = Connected
	
	sender = asyncore.dispatcher(map=server._map)
	sender.create_socket(socket.AF_INET, socket.SOCK_STREAM)
	sender.connect(("localhost", 31425))
	outgoing = EndPointChannel(sender, map=server._map)
	
	from time import sleep
	
	print "*** polling for half a second"
	for x in range(250):
		server.Pump()
		outgoing.Pump()
		sleep(0.001)

