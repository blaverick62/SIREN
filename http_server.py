#############################################################
# NAME: C1C Braden J Laverick                               #
# PROJECT: SIREN Project                                    #
# FILE: SIREN Server Classes - ftp_server.py             #
# DESCRIPTION:                                              #
# This file specifies the classes for the various control   #
# servers that SIREN implements.                            #
#############################################################

import socket, threading

class HTTPserverThread(threading.Thread):
    def __init__(self,(conn,addr)):
        self.conn=conn
        self.addr=addr
        threading.Thread.__init__(self)

    def run(self):
        while True:
            self.conn.recv(256)


class http_ctrl(threading.Thread):
    """
        Control server for the HTTP Protocol server
    """
    def __init__(self):
        self.port = 80
        self.buff = 4096
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind(socket.gethostname(), self.port)
        threading.Thread.__init__(self)

    def http_run(self):
        self.sock.listen(5)
        while 1:
            th = HTTPserverThread(self.sock.accept())
            th.start()
            pass

    def http_stop(self):
        self.sock.close()