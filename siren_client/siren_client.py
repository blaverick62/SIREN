#############################################################
# NAME: C1C Braden J Laverick                               #
# PROJECT: SIREN Project                                    #
# FILE: SIREN Server Classes - siren_client.py              #
# DESCRIPTION:                                              #
# This file receives commands and determines emulation on   #
# the detonation chamber                                    #
#############################################################

import socket, threading, os, sys
from subprocess import Popen, PIPE, STDOUT

class telnetClientThread(threading.Thread):
    def __init__(self,(conn,addr)):
        self.conn=conn
        self.addr=addr
        print("Connected with SIREN control at {}...".format(self.addr[0]))
        threading.Thread.__init__(self)


    def run(self):
        path = "/home/srodgers"
        while True:
            try:
                cmd = self.conn.recv(256)
                print(cmd)
                cmdlist = cmd.split(" ")
                if cmdlist[0] == "TERMINATE":
                    print("Session closed")
                    return
                if cmdlist[0] == "cd":
                    if cmdlist[1] == "..":
                        pathlist = path.split("/")
                        pathlist = pathlist[1:]
                        if len(pathlist) > 1:
                            pathlist = pathlist[:-1]
                        if len(pathlist) > 1:
                            path = "/".join(pathlist)
                        else:
                            path = pathlist[0]
                        if path[0] != "/":
                            path = "/" + path
                        self.conn.send(path + ";")
                    elif cmdlist[1] == ".":
                        self.conn.send(path + ";")
                    else:
                        if cmdlist[1][0] == '/':
                            if os.path.isdir(cmdlist[1]):
                                if "siren" not in cmdlist[1]:
                                    path = cmdlist[1]
                                    self.conn.send(path + ";")
                                else:
                                    self.conn.send(path + ";" + "bash: cd: " + cmdlist[1] + ": No such file or directory")
                            else:
                                self.conn.send("bash: cd: " + cmdlist[1] + ": No such file or directory")
                        else:
                            if os.path.isdir(path + "/" + cmdlist[1]):
                                if "siren" not in cmdlist[1]:
                                    path = path + "/" + cmdlist[1]
                                    self.conn.send(path + ";")
                                else:
                                    self.conn.send(path + ";" + "bash: cd: " + cmdlist[1] + ": No such file or directory")
                            else:
                                self.conn.send(path + ";" + "bash: cd: " + cmdlist[1] + ": No such file or directory")
                else:
                    proc = Popen("(cd " + path + " && " + cmd + ")", shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
                    cmdout = path + ";" + proc.stdout.read()
                    self.conn.send(cmdout)
            except socket.timeout:
                print("SIREN connection has timed out")
                return


    def stop(self):
        self.conn.close()


telsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
telsock.bind(('', 23))
telsock.listen(5)
threads = []

while 1:
    try:
        newconn = telsock.accept()
        print(newconn)
        th = telnetClientThread(newconn)
        threads.append(th)
        th.start()
    except KeyboardInterrupt:
        for i in threads:
            i.stop()
        sys.exit()

