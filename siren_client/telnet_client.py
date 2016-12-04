#############################################################
# NAME: C1C Braden J Laverick                               #
# PROJECT: SIREN Project                                    #
# FILE: SIREN Server Classes - telnet_server.py             #
# DESCRIPTION:                                              #
# This file specifies the classes for the various control   #
# servers that SIREN implements.                            #
#############################################################

import socket, threading, os
from subprocess import Popen, PIPE, STDOUT

class telnetClientThread(threading.Thread):
    def __init__(self,(conn,addr)):
        self.conn=conn
        self.addr=addr
        print("Connected with SIREN control at %s..." % self.conn)
        threading.Thread.__init__(self)


    def run(self):
        while True:
            try:
                cmd = self.conn.recv(256)
                print(cmd)
                if cmd[:2] == 'cd':
                    currpath = os.getcwd()
                    os.chdir(cmd[2:])
                    if os.getcwd() == currpath:
                        cmdout = "bash: cd: %s: No such file or directory"
                        self.conn.send(cmdout.encode(encoding='utf-8'))
                else:
                    proc = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
                    cmdout = proc.stdout.read()
                    self.conn.send(cmdout.encode(encoding='utf-8'))
            except socket.error, socket.timeout:
                print("Connection with SIREN has timed out")
                break


telsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
telsock.bind(('', 23))
telsock.listen(5)
telsock.settimeout(240)
while 1:
    try:
        newconn = telsock.accept()
        print(newconn)
        th = telnetClientThread(newconn)
        th.start()
        pass
    except KeyboardInterrupt:
        break
