#############################################################
# NAME: C1C Braden J Laverick                               #
# PROJECT: SIREN Project                                    #
# FILE: SIREN Logging Facility - logger.py                  #
# DESCRIPTION:                                              #
# This file collects logging data from the honeypot         #
# listeners and packages them for the mysql database.       #
#############################################################

import MySQLdb, threading, socket, Queue

class logger_send_thread(threading.Thread):

    def __init__(self, data):
        threading.Thread.__init__(self)
        self.data = data

class logger(threading.Thread):

    def __init__(self, username, password):
        threading.Thread.__init__(self)
        self.bufferList = buffer
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind(('localhost', 1337))
        self.db = MySQLdb.connect(host="localhost",
                                  user=username,
                                  passwd=password,
                                  db="siren_db")

    def run(self):
        self.sock.listen(5)
        while(1):
            th = logger_rec_thread(self.sock.accept())
            th.start()


class logger_rec_thread(threading.Thread):

    def __init__(self, (conn, addr)):
        threading.Thread.__init__(self)
        self.buffer = buffer
        self.conn = conn
        self.addr = addr

    def run(self):
        data = self.conn.recv(4096)
