#############################################################
# NAME: C1C Braden J Laverick                               #
# PROJECT: SIREN Project                                    #
# FILE: SIREN Server Classes - SIREN_SERVERS.py             #
# DESCRIPTION:                                              #
# This file specifies the classes for the various control   #
# servers that SIREN implements.                            #
#############################################################

import socket
from thread import*

class http_ctrl:
    """
        Control server for the HTTP Protocol server
    """
    def __init__(self):
        self.port = 80
        self.buff = 4096
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def http_receive(self, conn):
        while True:
            data = conn.recv(self.buff)
        conn.close()


    def http_bind(self):
        self.sock.bind(socket.gethostname(), self.port)
        self.sock.listen()
        while 1:
            (conn, address) = self.sock.accept
            print("New client connected")
            start_new_thread(self.http_receive(conn))
        self.sock.close()

class ftp_ctrl:
    """
        Control server for the HTTP Protocol server
    """
    def __init__(self):
        self.ctlPort = 21
        self.dataPort = 20
        self.buff = 4096
        self.ctlSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.dataSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def http_receive(self, conn):
        data = ""
        while True:
            data = conn.recv(self.buff)
        conn.close()
        return data


    def http_bind(self):
        self.ctlSock.bind(socket.gethostname(), self.ctlPort)
        self.ctlSock.listen()
        while 1:
            (conn, address) = self.ctlSock.accept
            print("New client connected")
            start_new_thread(self.http_receive, conn)
        self.ctlSock.close()