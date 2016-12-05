#############################################################
# NAME: C1C Braden J Laverick                               #
# PROJECT: SIREN Project                                    #
# FILE: SIREN Logging Facility - local.py                   #
# DESCRIPTION:                                              #
# This file defines the socket listener for logging         #
# communication within siren                                #
#############################################################

import threading, socket


class logger_sock(threading.Thread):

    def __init__(self, buffer, mutex):
        threading.Thread.__init__(self)
        self.bufferList = buffer
        self.mutex = mutex
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind(('localhost', 1337))


    def run(self):
        self.sock.listen(5)
        while (1):
            try:
                th = logger_receive(self.sock.accept(), self.bufferList, self.mutex)
                th.start()
            except socket.error:
                print("Socket closed.")
                break
            except KeyboardInterrupt:
                print("Closing logging socket...")
                break
        self.sock.close()

    def stop(self):
        self.sock.close()


class logger_receive(threading.Thread):

    def __init__(self, (conn, addr), buffer, mutex):
        threading.Thread.__init__(self)
        self.buffer = buffer
        self.mutex = mutex
        self.conn = conn
        self.addr = addr

    def run(self):
        while 1:
            try:
                data = self.conn.recv(4096)
                self.mutex.acquire()
                try:
                    self.buffer.put(data)
                finally:
                    self.mutex.release()
            except socket.error:
                print("Connection with sensor lost")
                break
            except KeyboardInterrupt:
                print("Closing logging...")
                break