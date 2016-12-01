#############################################################
# NAME: C1C Braden J Laverick                               #
# PROJECT: SIREN Project                                    #
# FILE: SIREN Logging Facility - logger.py                  #
# DESCRIPTION:                                              #
# This file collects logging data from the honeypot         #
# listeners and packages them for the mysql database.       #
#############################################################

import MySQLdb, threading, socket, Queue


class logger(threading.Thread):

    def __init__(self, username, password):
        threading.Thread.__init__(self)
        self.buffer = Queue.Queue()
        self.sock = logger_sock(self.buffer)
        self.store = logger_store(self. buffer, username, password)

    def run(self):
        self.sock.start()
        self.store.start()


# class logger_db(threading.Thread):
#
#    def __init__(self, username, password):
#        threading.Thread.__init__(self)
#        self.db = MySQLdb.connect(host="localhost",
#                             user=username,
#                             passwd=password,
#                             db="siren_db")


class logger_store(threading.Thread):

    def __init__(self, buffer, username, password):
        threading.Thread.__init__(self)
        self.buffer = buffer
        self.db = MySQLdb.connect(host="localhost",
                                  user=username,
                                  passwd=password,
                                  db="siren_db")
        self.cursor = self.db.cursor()
        #for line in open("../siren_db/siren_schema.sql"):
        #    self.cursor.execute(line)

    def run(self):
        while(1):
            if(self.buffer.empty() == False):
                data = self.buffer.get()
                print(data + " - From logger")

class logger_sock(threading.Thread):

    def __init__(self, buffer):
        threading.Thread.__init__(self)
        self.bufferList = buffer
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind(('localhost', 1337))


    def run(self):
        self.sock.listen(5)
        while (1):
            th = logger_receive(self.sock.accept(), self.bufferList)
            th.start()


class logger_receive(threading.Thread):

    def __init__(self, (conn, addr), buffer):
        threading.Thread.__init__(self)
        self.buffer = buffer
        self.conn = conn
        self.addr = addr

    def run(self):
        data = self.conn.recv(4096)
        self.buffer.put(data)


