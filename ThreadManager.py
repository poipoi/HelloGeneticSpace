import threading
import time
from queue import Queue


class Ticker:
	def __init__(self, span, queue, name):
		self.span = span
		self.queue = queue
		self.name = name

	def start(self):
		self.__run()
		return self

	def stop(self):
		self.t.cancel()
		return self
	
	def __run(self):
		self.t = threading.Timer(self.span, self.__run)
		self.t.daemon = True
		self.t.start()
		self.queue.put(self.name)

class Thread:
	def __init__(self, target, queue):
		self.target = target
		self.isFinish = False
		self.q = queue
		self.t = threading.Thread(target = self.__run)
		self.t.daemon = True

	def start(self):
		self.t.start()
		return self

	def stop(self):
		self.isFinish = True
		self.q.put(None)
		self.t.join()
		return self

	def __run(self):
		while not self.isFinish:
			arg = self.q.get()
			if arg != None:
				self.target(arg)
			

if __name__ == '__main__':
	q = Queue()

	def run(arg):
		if arg == "tick":
			print("tick")
		elif arg == "event":
			print("event")

	tick = Ticker(1, q, "tick").start()
	t = Thread(run, q).start()

	time.sleep(5)
	q.put("event")
	time.sleep(5)
	q.put("event")

	tick.stop()
	t.stop()
