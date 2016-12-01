#############################################################
# NAME: C1C Braden J Laverick                               #
# PROJECT: SIREN Project                                    #
# FILE: SIREN Server Classes - telnet_server.py             #
# DESCRIPTION:                                              #
# This file specifies the classes for the various control   #
# servers that SIREN implements.                            #
#############################################################

import socket, threading, sys


class telnetServerThread(threading.Thread):
    def __init__(self,(conn,addr), linaddr, winaddr):
        self.conn=conn
        self.addr=addr
        threading.Thread.__init__(self)
        #self.winsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.linsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.logsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # winconn = self.winsock.connect((winaddr, 23))
        try:
            self.logsock.connect('localhost', 1337)
        except socket.error:
            print("Failed to connect to logging facility")
        try:
            self.linsock.connect((linaddr, 23))
        except socket.error:
            print("Failed to connect to detonation chamber")


        self.linsock.settimeout(30)

    def run(self):
        self.conn.send(b'Connected, exit character is ^]\r\n')
        while True:
            try:
                data = self.conn.recv(256)
                self.logsock.send(data)
            except socket.timeout:
                print("Connection with attacker has timed out")
                data = "^]\r\n"
            if (data == "^]\r\n"):
                break
            #self.winconn.sendall(data)
            self.linsock.sendall(data)
            try:
                response = self.linsock.recv(1024)
            except socket.timeout:
                response = "Connection with host has timed out"
            self.conn.send(response.encode(encoding='utf-8'))
        self.linsock.close()



class telnet_ctrl(threading.Thread):
    """
        Control server for the HTTP Protocol server
    """
    def __init__(self):
        self.port = 23
        self.buff = 4096
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(240)
        detaddrs = open("siren.config", mode="r")
        addrs = detaddrs.read()
        spaddrs = addrs.split('\n')
        self.linaddr = spaddrs[0]
        print(self.linaddr)
        self.winaddr = spaddrs[1]
        print("Detonation chamber at %s..." % self.linaddr)
        detaddrs.close()
        try:
            print("Starting Telnet Server at %s..." % socket.gethostname())
            self.sock.bind(('', self.port))
        except Exception as e:
            print("Telnet Server failed to bind to port...")
            sys.exit()

        threading.Thread.__init__(self)

    def run(self):
        self.sock.listen(5)
        while 1:
            try:
                newconn = self.sock.accept()
                print(newconn)
                try:
                    th = telnetServerThread(newconn, self.linaddr, self.winaddr)
                except socket.error:
                    break
                th.start()
                pass
            except KeyboardInterrupt:
                break
        self.sock.close()

    def stop(self):
        self.sock.close()