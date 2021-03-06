#############################################################
# NAME: C1C Braden J Laverick                               #
# PROJECT: SIREN Project                                    #
# FILE: SIREN Server Classes - telnet_server.py             #
# DESCRIPTION:                                              #
# This file specifies the classes for the various control   #
# servers that SIREN implements.                            #
#############################################################

import socket, threading, datetime, sys, traceback, ConfigParser
import netifaces as ni


class telnetServerThread(threading.Thread):

    def __init__(self,(conn,addr), linaddr, winaddr, iface, detuser):
        self.conn=conn
        self.addr=addr
        self.iface = iface
        self.detuser = detuser
        threading.Thread.__init__(self)
        self.linsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.logsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
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
        self.destip = ni.ifaddresses(self.iface)[2][0]['addr']
        ip = self.addr[0]
        remoteport = self.addr[1]
        self.endtime = self.starttime
        self.logsock.send("SESSION;{};{};{};{};{};{};{}".format(self.starttime, self.endtime, ip, self.destip, 'telnet', 23, remoteport))
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
            with open('docs/users.txt', mode='r') as users:
                for line in users:
                    auth = line.split(':')
                    if(username == auth[0] and password == auth[1]):
                        self.username = username
                        success = 1
            self.logsock.send("AUTH;{};{};{};{};{}".format(self.starttime, success, username, password,
                                                           datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            tries += 1
        if success == 0:
            self.conn.send("Unauthorized")
            self.endtime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.logsock.send("UPDATE;{};{}".format(self.endtime, self.starttime))
            return
        self.linsock.send("pwd")
        try:
            resp = self.linsock.recv(256)
            self.conn.send(resp.split(";")[1].replace(self.detuser, self.username))
        except socket.timeout as e:
            print("Telnet timed out: " + str(e))
            traceback.print_exc()
            sys.exit(1)



        # Receive loop and emulator
        while True:

            try:
                data = self.conn.recv(4096)
            except socket.timeout:
                print("Connection closed for unknown reason by attacker")
                self.endtime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                self.logsock.send("UPDATE;{};{}".format(self.endtime, self.starttime))
                self.linsock.send("TERMINATE")
                self.logsock.send("TERMINATE")
                self.linsock.close()
                self.logsock.close()
                sys.exit(0)


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


                self.linsock.sendall(data)
                try:
                    response = self.linsock.recv(20000)
                    resplist = response.split(";")
                    chanresponse = '\r\n'.join(resplist[1].split('\n'))
                    chanresponse = chanresponse.replace('\n'+self.detuser, '\n' + self.username)
                    chanresponse = chanresponse.replace(self.detuser+'\n', self.username + '\n')
                    chanresponse = chanresponse.replace(self.detuser, self.username)
                except socket.timeout:
                    print("Telnet detonation chamber has timed out")
                    self.endtime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    self.logsock.send("UPDATE;{};{}".format(self.endtime, self.starttime))
                    self.logsock.send("TERMINATE")
                    self.logsock.close()
                    sys.exit(0)
                if len(resplist) > 1:
                    self.conn.send(resplist[1])


    def stop(self):
        self.linsock.send("TERMINATE")
        self.logsock.send("TERMINATE")
        self.linsock.close()
        self.logsock.close()








class telnet_ctrl(threading.Thread):
    """
        Control server for the telnet Protocol server
    """
    def __init__(self):
        self.port = 23
        self.buff = 4096
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(30)
        config = ConfigParser.ConfigParser()
        config.read('docs/siren.cfg')
        self.iface = config.get('Interfaces', 'interface')
        self.linaddr = config.get('Detonation Chamber', 'host')
        self.winaddr = '0.0.0.0'
        self.detuser = config.get('Detonation Chamber', 'user')
        try:
            print("Starting Telnet Server at %s..." % ni.ifaddresses(self.iface)[2][0]['addr'])
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
                newconn = self.sock.accept()
                print(newconn[1][0])
                th = telnetServerThread(newconn, self.linaddr, self.winaddr, self.iface, self.detuser)
                th.start()
                self.threads.append(th)
            except KeyboardInterrupt:
                print("Keyboard interrupt caught")
                self.stop()
                sys.exit()
            except socket.timeout:
                pass

    def stop(self):
        for th in self.threads:
            th.stop()
        self.sock.close()