#############################################################
# NAME: C1C Braden J Laverick                               #
# PROJECT: SIREN Project                                    #
# FILE: SIREN Logging Facility - logger.py                  #
# DESCRIPTION:                                              #
# This file collects logging data from the honeypot         #
# listeners and packages them for the mysql database.       #
#############################################################

import threading, socket, Queue
import MySQLdb
from threading import Lock

class logger(threading.Thread):

    def __init__(self, username, password):
        threading.Thread.__init__(self)
        self.buffer = Queue.Queue()
        self.mutex = Lock()
        self.sock = logger_sock(self.buffer, self.mutex)
        self.store = logger_store(self. buffer, self.mutex, username, password)

    def run(self):
        self.sock.start()
        self.store.start()

    def stop(self):
        self.sock.stop()

# class logger_db(threading.Thread):
#
#    def __init__(self, username, password):
#        threading.Thread.__init__(self)
#        self.db = MySQLdb.connect(host="localhost",
#                             user=username,
#                             passwd=password,
#                             db="siren_db")


class logger_store(threading.Thread):

    def __init__(self, buffer, mutex, username, password):
        threading.Thread.__init__(self)
        self.buffer = buffer
        self.mutex = mutex
        self.db = MySQLdb.connect(host="localhost",
                                  user=username,
                                  passwd=password,
                                  db="siren_db")
        self.cursor = self.db.cursor()
        for line in open("log/siren_schema.sql"):
            self.cursor.execute(line)

    def run(self):
        while(1):
            if(self.buffer.empty() == False):
                self.mutex.acquire()
                try:
                    data = self.buffer.get()
                finally:
                    self.mutex.release()
                print(data + " - From logger")
                args = data.split(';')
                if args[0] == "SESSION":
                    self.cursor.execute("insert into SESSION values(NULL,'{}','{}');".format(args[1], args[2]))
                if args[0] == "INPUT":
                    id = self.cursor.execute("select session_id from SESSION where ip='{}';".format(args[1]))
                    self.cursor.execute("insert into INPUT values(NULL,{},'{}','{}')".format(id,args[2],args[3]))
                self.db.commit()



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



