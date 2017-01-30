#############################################################
# NAME: C1C Braden J Laverick                               #
# PROJECT: SIREN Project                                    #
# FILE: SIREN Server Classes - telnet_server.py             #
# DESCRIPTION:                                              #
# This file specifies the classes for the various control   #
# servers that SIREN implements.                            #
#############################################################

import socket, threading, datetime, sys


class telnetServerThread(threading.Thread):

    def __init__(self,(conn,addr), linaddr, winaddr, det):
        self.conn=conn
        self.addr=addr
        self.det=det
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
            self.stop()
        self.linsock.settimeout(30)


    def run(self):

        # Authorization and brute force logger
        self.starttime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.destip = socket.gethostbyname(socket.gethostname())
        ip = self.addr[0]
        remoteport = self.addr[1]
        self.endtime = self.starttime
        self.logsock.send("SESSION;{};{};{};{};{};{}".format(self.starttime, self.endtime, ip, self.destip, 'telnet', 23, remoteport))
        success = 0
        tries = 0
        try:
            self.conn.recv(256)
        except socket.timeout:
            self.linsock.close()
            self.endtime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.logsock.send("".format(self.starttime, self.endtime, ip, 'telnet', remoteport))
            return
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
            self.logsock.send("AUTH;{};{};{};{};{}".format(self.starttime, success, username, password,
                                                           datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            tries += 1
        if success == 0:
            self.conn.send("Unauthorized")
            self.endtime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.logsock.send("UPDATE;{};{}".format(self.endtime, self.starttime))
            return
        if self.det == 'l':
            self.linsock.send("pwd")
        else:
            self.linsock.send('cd')
        resp = self.linsock.recv(256)
        self.conn.send(resp)


        # Receive loop and emulator
        while True:

            try:
                data = self.conn.recv(4096)
            except socket.timeout:
                print("Connection closed for unknown reason by attacker")
                self.endtime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                self.logsock.send("UPDATE;{};{}".format(self.endtime, self.starttime))
                self.linsock.close()
                return


            timestmp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            data = data[:-2]
            if len(data) > 0:
                if data[0] == "'":
                    print("SQL Injection detected! Isolating threat...")
                    with open('threatlog.txt', mode='a') as threatlog:
                        threatlog.write(ip + ": " + data + '\n')
                else:
                    self.logsock.send("INPUT;{};{};{}".format(self.starttime, timestmp, data))
                print(data)
                # self.winconn.sendall(data)


                if data[:2] == 'cd':
                    self.linsock.sendall(data)


                elif data[:3] == 'pwd' and self.det == 'l':
                    self.linsock.sendall(data)
                    try:
                        response = self.linsock.recv(20000)
                    except socket.timeout:
                        print("Connection with detonation chamber has timed out")
                        self.endtime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        self.logsock.send("UPDATE;{};{}".format(self.endtime, self.starttime))
                        return
                    self.conn.send(response)


                elif data[:2] == 'ls' and self.det == 'l':
                    self.linsock.sendall(data)
                    try:
                        response = self.linsock.recv(20000)
                    except socket.timeout:
                        print("Connection with detonation chamber has timed out")
                        self.endtime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        self.logsock.send("UPDATE;{};{}".format(self.endtime, self.starttime))
                        self.linsock.close()
                        return
                    self.conn.send(response)


                elif data[:5] == 'touch' and self.det == 'l':
                    self.linsock.sendall(data)


                elif data[:4] == 'echo':
                    self.linsock.sendall(data)
                    try:
                        response = self.linsock.recv(20000)
                    except socket.timeout:
                        print("Connection with detonation chamber has timed out")
                        self.endtime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        self.logsock.send("UPDATE;{};{}".format(self.endtime, self.starttime))
                        return
                    self.conn.send(response)


                else:
                    self.linsock.sendall("echo 'command not found'")


    def stop(self):
        self.linsock.send("TERMINATE")
        self.linsock.close()
        self.logsock.close()








class telnet_ctrl(threading.Thread):
    """
        Control server for the telnet Protocol server
    """
    def __init__(self, det):
        self.port = 23
        self.buff = 4096
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(30)
        self.det = det
        detaddrs = open("siren.config", mode="r")
        addrs = detaddrs.read()
        spaddrs = addrs.split('\n')
        self.linaddr = spaddrs[0]
        print(self.linaddr)
        self.winaddr = spaddrs[1]
        print("Detonation chamber at %s..." % self.linaddr)
        detaddrs.close()
        try:
            print("Starting Telnet Server at %s..." % socket.gethostbyname(socket.gethostname()))
            self.sock.bind(('', self.port))
        except Exception as e:
            print("Telnet Server failed to bind to port...")
            return

        threading.Thread.__init__(self)

    def run(self):
        self.sock.listen(50)
        self.threads = []
        while 1:
            try:
                try:
                    newconn = self.sock.accept()
                    print(newconn[1][0])
                    th = telnetServerThread(newconn, self.linaddr, self.winaddr, self.det)
                    th.start()
                    self.threads.append(th)
                except (socket.timeout, socket.gaierror) as e:
                    print("Exception caught: " + str(e))
                    endtime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    th.logsock.send("UPDATE;{};{}".format(endtime,th.starttime))
                    th.stop()

            except KeyboardInterrupt:
                print("Keyboard interrupt caught")
                self.stop()
                sys.exit()
            except socket.gaierror:
                print("General Exception in telnet control")
                self.stop()
                sys.exit()

    def stop(self):
        for th in self.threads:
            th.stop()
        self.sock.close()