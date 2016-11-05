#############################################################
# NAME: C1C Braden J Laverick                               #
# PROJECT: SIREN Project                                    #
# FILE: SIREN Server Classes - telnet_server.py             #
# DESCRIPTION:                                              #
# This file specifies the classes for the various control   #
# servers that SIREN implements.                            #
#############################################################

import socket, threading, sys, os

class telnetServerThread(threading.Thread):
    def __init__(self,(conn,addr), linaddr, winaddr):
        self.conn=conn
        self.addr=addr
        threading.Thread.__init__(self)
        #self.winsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.linsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #self.winconn = self.winsock.connect((winaddr, 23))
        print(linaddr)
        self.linconn = self.linsock.connect((linaddr, 1234))

    def run(self):

        while True:
            data = self.conn.recv(256)
            print(data)
            #self.winconn.sendall(data)
            self.linconn.sendall(data)
            self.conn.send(b'Message received fam!\r\n')


class telnet_ctrl(threading.Thread):
    """
        Control server for the HTTP Protocol server
    """
    def __init__(self):
        self.port = 2023
        self.buff = 4096
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        detaddrs = open("siren.config", mode="r")
        self.linaddr = detaddrs.readline()
        self.winaddr = detaddrs.readline()
        detaddrs.close()
        try:
            print("Starting Telnet Server...")
            self.sock.bind((socket.gethostname(), self.port))
        except Exception as e:
            print("Telnet Server failed to bind to port...")
            sys.exit()

        threading.Thread.__init__(self)

    def run(self):
        self.sock.listen(5)
        while 1:
            th = telnetServerThread(self.sock.accept(), self.linaddr, self.winaddr)
            th.start()
            pass

    def stop(self):
        self.sock.close()