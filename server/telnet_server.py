#############################################################
# NAME: C1C Braden J Laverick                               #
# PROJECT: SIREN Project                                    #
# FILE: SIREN Server Classes - telnet_server.py             #
# DESCRIPTION:                                              #
# This file specifies the classes for the various control   #
# servers that SIREN implements.                            #
#############################################################

import socket, threading, sys, datetime, signal


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
            self.logsock.connect(('127.0.0.1', 1337))
        except socket.error:
            print("Failed to connect to logging facility")
        try:
            self.linsock.connect((linaddr, 23))
        except socket.error:
            print("Failed to connect to detonation chamber")


        self.linsock.settimeout(240)


    def run(self):
        starttime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        ip = self.addr[0]
        self.logsock.send("SESSION;{};{}".format(starttime, ip))
        try:
            username = ""
            password = ""
            success = 0
            tries = 0
            self.conn.recv(256)
            while(success == 0 and tries < 3):
                self.conn.send("login: ")
                username = self.conn.recv(256)
                username = username[:-2]
                self.conn.send("password: ")
                password = self.conn.recv(256)
                password = password[:-2]
                with open('server/users.txt', mode='r') as users:
                    for line in users:
                        auth = line.split(':')
                        if(username == auth[0] and password == auth[1]):
                            success = 1
                tries += 1
            self.logsock.send("AUTH;{};{};{};{};{}".format(starttime,success,username,password,datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            self.linsock.send("pwd")
            resp = self.linsock.recv(256)
            self.conn.send(resp)
            if success == 0:
                return
        except socket.error:
            print("Connection closed")
            return
        while True:
            try:
                data = self.conn.recv(4096)
                timestmp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                data = data[:-2]
                self.logsock.send("INPUT;{};{};{}".format(starttime, timestmp, data))
                self.logsock.send(data)
                print(data)
                # self.winconn.sendall(data)
                self.linsock.sendall(data)
            except socket.error:
                print("Connection closed")
                return
            try:
                response = self.linsock.recv(20000)

            except socket.timeout:
                print("Connection with host has timed out")
                return
            self.conn.send(response)
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
            return

        threading.Thread.__init__(self)

    def run(self):
        self.sock.listen(5)
        while 1:
            try:
                newconn = self.sock.accept()
                print(newconn)
                try:
                    th = telnetServerThread(newconn, self.linaddr, self.winaddr)
                    th.start()
                except socket.error:
                    print("Socket error")
                    break
            except KeyboardInterrupt:
                print("Keyboard interrupt caught")
                self.sock.close()
                return
            except Exception:
                print("General Exception in telnet control")
                self.sock.close()
                return

        self.sock.close()

    def stop(self):
        self.sock.close()