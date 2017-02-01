#############################################################
# NAME: C1C Braden J Laverick                               #
# PROJECT: SIREN Project                                    #
# FILE: SIREN Logging Facility - local.py                   #
# DESCRIPTION:                                              #
# This file defines the socket listener for logging         #
# communication within siren                                #
#############################################################

import threading, socket, sys


class tel_logger_sock(threading.Thread):

    def __init__(self, buffer, mutex):
        threading.Thread.__init__(self)
        self.bufferList = buffer
        self.mutex = mutex
        self.telsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.telsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.telsock.bind(('127.0.0.1', 1337))


    def run(self):
        self.telsock.listen(50)
        self.threads = []
        while (1):
            try:
                th = logger_receive(self.telsock.accept(), self.bufferList, self.mutex)
                self.threads.append(th)
                th.start()
            except socket.error:
                print("Socket closed.")
                break
            except KeyboardInterrupt:
                print("Closing logging socket...")
                break
        self.telsock.close()

    def stop(self):
        for i in self.threads:
            i.stop()
        self.telsock.close()
        sys.exit(0)


class ssh_logger_sock(threading.Thread):
    def __init__(self, buffer, mutex):
        threading.Thread.__init__(self)
        self.bufferList = buffer
        self.mutex = mutex
        self.sshsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sshsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sshsock.bind(('127.0.0.1', 1338))


    def run(self):
        self.sshsock.listen(50)
        self.threads = []
        while (1):
            try:
                th = logger_receive(self.sshsock.accept(), self.bufferList, self.mutex)
                self.threads.append(th)
                th.start()
            except socket.error:
                print("Socket closed.")
                break
            except KeyboardInterrupt:
                print("Closing logging socket...")
                break
        self.sshsock.close()

    def stop(self):
        for i in self.threads:
            i.stop()
        self.sshsock.close()
        sys.exit(0)

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
                if data == "TERMINATE":
                    return
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

    def stop(self):
        sys.exit(0)