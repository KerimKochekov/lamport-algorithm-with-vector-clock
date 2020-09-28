from multiprocessing import Process, Pipe
from os import getpid
from datetime import datetime


def local_time(counter):
	return ' (LAMPORT_TIME={}, LOCAL_TIME={})'.format(counter, datetime.now())


def update(recv_time_stamp, counter):
	for id  in range(len(counter)):
		counter[id] = max(recv_time_stamp[id], counter[id])
	return counter

def event(pid, counter):
	counter[pid] += 1
	print('Event in {} !'.format(pid) + local_time(counter))
	return counter

def send(pipe, pid, counter):
	counter[pid] += 1
	pipe.send(('Empty shell', counter))
	print('Sent from ' + str(pid) + local_time(counter))
	return counter

def receive(pipe, pid, counter):
	_, timestamp = pipe.recv()
	counter = update(timestamp, counter)
	print('Received at ' + str(pid) + local_time(counter))
	return counter

def A(ab):
	pid = 0
	counter = [0, 0, 0]
	counter = send(ab, pid, counter)
	counter = event(pid, counter)
	counter = event(pid, counter)
	counter = send(ab, pid, counter)
	counter = event(pid, counter)
	counter = receive(ab, pid, counter)
	counter = receive(ab, pid, counter)

def B(ba, bc):
	pid = 1
	counter = [0, 0, 0]
	counter = receive(bc, pid, counter)
	counter = receive(bc, pid, counter)
	counter = receive(ba, pid, counter)
	counter = event(pid, counter)
	counter = send(bc, pid, counter)
	counter = receive(ba, pid, counter)
	counter = send(ba, pid, counter)
	counter = send(ba, pid, counter)

def C(cb):
	pid = 2
	counter = [0, 0, 0]
	counter = send(cb, pid, counter)
	counter = event(pid, counter)
	counter = send(cb, pid, counter)
	counter = receive(cb, pid, counter)

if __name__ == '__main__':
	ab, ba = Pipe()
	bc, cb = Pipe()

	process1 = Process(target=A, args=(ab,))
	process2 = Process(target=B, args=(ba, bc))
	process3 = Process(target=C, args=(cb,))

	process3.start()
	process1.start()
	process2.start()

	process2.join()
	process1.join()
	process3.join()
