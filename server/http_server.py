#############################################################
# NAME: C1C Braden J Laverick                               #
# PROJECT: SIREN Project                                    #
# FILE: SIREN Server Classes - http_server.py               #
# DESCRIPTION:                                              #
# This file specifies the classes for the various control   #
# servers that SIREN implements.                            #
#############################################################

import socket, threading, sys
from base import base
from detonation.det_routes import *

class HTTPserverThread(threading.Thread):
    def __init__(self,(conn,addr),lindetconn,windetconn):
        self.conn=conn
        self.addr=addr
        self.lindetconn = lindetconn
        self.windetconn = windetconn
        threading.Thread.__init__(self)

    def run(self):

        while True:
            data = self.conn.recv(256)
            print(data)
            self.conn.send(b'Message received fam!\r\n')
            self.lindetconn.sendall(data)


class http_ctrl(base, threading.Thread):
    """
        Control server for the HTTP Protocol server
    """
    def __init__(self):
        self.port = 4230
        self.buff = 4096
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            print("Starting HTTP Server...")
            self.sock.bind((socket.gethostname(), self.port))
        except Exception as e:
            print("HTTP Server failed to bind to port...")
            sys.exit()

        threading.Thread.__init__(self)
        base.__init__(self, winDet=super, linDet=super)

    def run(self):
        self.sock.listen(5)
        while 1:
            th = HTTPserverThread(self.sock.accept(), self.linDet.httpconn, self.winDet.httpconn)
            th.start()
            pass

    def stop(self):
        self.sock.close()