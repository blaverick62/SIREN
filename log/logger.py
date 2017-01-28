#############################################################
# NAME: C1C Braden J Laverick                               #
# PROJECT: SIREN Project                                    #
# FILE: SIREN Logging Facility - logger.py                  #
# DESCRIPTION:                                              #
# This file defines the master/starter class for the SIREN  #
# text and MySQL logging facility                           #
#############################################################

import threading, Queue
from threading import Lock
from local import logger_sock
from db import logger_store


class logger(threading.Thread):

    def __init__(self, ip, username, password):
        threading.Thread.__init__(self)
        self.buffer = Queue.Queue()
        self.mutex = Lock()
        self.sock = logger_sock(self.buffer, self.mutex)
        self.store = logger_store(self. buffer, self.mutex, ip, username, password)

    def run(self):
        self.sock.start()
        self.store.start()

    def stop(self):
        self.sock.stop()



