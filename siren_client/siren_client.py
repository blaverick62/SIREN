#############################################################
# NAME: C1C Braden J Laverick                               #
# PROJECT: SIREN Project                                    #
# FILE: SIREN Server Classes - siren_client.py              #
# DESCRIPTION:                                              #
# This file receives commands and determines emulation on   #
# the detonation chamber                                    #
#############################################################

import socket, threading, os, sys, random
from subprocess import Popen, PIPE, STDOUT
from time import sleep

class telnetClientThread(threading.Thread):
# Handler thread for siren client
# Takes in commands from control, executes them, sends back STDOUT
# Whitelists and emulates certain commands

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
                # Close on end message from control
                if cmdlist[0] == "TERMINATE":
                    print("Session closed")
                    return

                # Check for change directory
                # Emulates cd by parsing input to build a string representing the path
                # Runs every other command with path included to provide realism
                if cmdlist[0] == "cd":
                    # Check for parent
                    if cmdlist[1] == "..":
                        # Split path and remove last element of array to get parent
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
                    # Do nothing for current
                    elif cmdlist[1] == ".":
                        self.conn.send(path + ";")
                    else:
                        # Clean path for detonation chamber use
                        cmdlist[1] = cmdlist[1].replace("admin", "srodgers")
                        if cmdlist[1][0] == '/':
                            # Check if path exists from root
                            if os.path.isdir(cmdlist[1]):
                                # Don't allow access into siren directories
                                if "siren" not in cmdlist[1]:
                                    path = cmdlist[1]
                                    # Change path to cd path
                                    self.conn.send(path + ";")
                                else:
                                    self.conn.send(path + ";" + "bash: cd: " + cmdlist[1] + ": No such file or directory")
                            else:
                                self.conn.send("bash: cd: " + cmdlist[1] + ": No such file or directory")
                        else:
                            # Check if path exists from current
                            if os.path.isdir(path + "/" + cmdlist[1]):
                                if "siren" not in cmdlist[1]:
                                    # Change path to cd path plus current
                                    path = path + "/" + cmdlist[1]
                                    self.conn.send(path + ";")
                                else:
                                    self.conn.send(path + ";" + "bash: cd: " + cmdlist[1] + ": No such file or directory")
                            else:
                                self.conn.send(path + ";" + "bash: cd: " + cmdlist[1] + ": No such file or directory")
                # Check for cat of password file
                elif cmdlist[0] == "cat" and (cmdlist[1] == "/etc/passwd" or cmdlist[1] == "passwd" or cmdlist[1] == "/etc/passwd-" or cmdlist[1] == "passwd-"):
                    # Read in and send back fake password file
                    with open('sirenpass.txt', mode='r') as f:
                        falsepass = f.read()
                    self.conn.send(path + ";" + falsepass)
                # Catch sudo and let them know that's not cool
                elif cmdlist[0] == "sudo" or cmdlist[0] == "su":
                    self.conn.send(path + ";" + "lol yeah nah m8 ill fuckin nip ya")
                # Check for netstat
                elif cmdlist[0] == "netstat":
                    # Print back dynamic active connections and static UDP connections
                    active = "Active Internet connections (w/o servers)\nProto\tRecv-Q\tSend-Q\tLocal Address\t\tForeign Address\t\tState\ntcp\t0\t0\t"+self.addr[0]+":23\t"+cmdlist[1]+":telnet\tESTABLISHED\n"
                    with open('netout.txt', mode='r') as f:
                        passive = f.read()
                    cmdout = active + passive
                    self.conn.send(path + ";" + cmdout)
                # Check for ping
                elif cmdlist[0] == "ping":
                    print("ping caught")
                    # Open error file
                    with open('pingerr.txt', mode='r') as f:
                        pingerr = f.read()
                    # Catch count option
                    if cmdlist[1] == "-c":
                        print("count argument")
                        try:
                            errflg = 0
                            try:
                                # check that count is a number
                                int(cmdlist[2])
                            except ValueError:
                                errflg = 1
                            if errflg == 0:
                                # Actually ping, but only once
                                try:
                                    pingresp = os.system("ping -c 1 " + cmdlist[3])
                                except IndexError:
                                    self.conn.send(path + ";" + pingerr)
                                    continue
                                if pingresp == 0:
                                    cmdout = "PING "+ cmdlist[3] + "56(84) bytes of data."
                                    # Generate lifelike ping response
                                    for i in range(1, int(cmdlist[2]) + 1):
                                        pingtime = random.random() * 30 + 40
                                        sleep(pingtime / 1000)
                                        cmdout = cmdout + "\n64 bytes from " + cmdlist[3] + ": icmp_seq=1 ttl=128 time=" + str(pingtime) + " ms"
                                    self.conn.send(path + ";" + cmdout)
                                else:
                                    sleep(15)
                                    self.conn.send(path + ";" + "ping: unknown host " + cmdlist[3])
                            else:
                                self.conn.send(path + ";" + pingerr)
                        except IndexError:
                            self.conn.send(path + ";" + pingerr)
                            continue
                    elif cmdlist[1][0] == "-":
                        # Don't allow other options
                        print("other argument")
                        self.conn.send(path + ";" + pingerr)
                    else:
                        # Default packets to 4
                        print("no argument")
                        try:
                            pingresp = os.system("ping -c 1 " + cmdlist[1])
                        except IndexError:
                            self.conn.send(path + ";" + pingerr)
                            continue
                        if pingresp == 0:
                            cmdout = "PING " + cmdlist[1] + "56(84) bytes of data."
                            for i in range(1, 5):
                                pingtime = random.random() * 30 + 40
                                cmdout = cmdout + "\n64 bytes from " + cmdlist[1] + ": icmp_seq=1 ttl=128 time=" + str(
                                    pingtime) + " ms"
                            self.conn.send(path + ";" + cmdout)
                        else:
                            sleep(15)
                            self.conn.send(path + ";" + "ping: unknown host " + cmdlist[1])
                else:
                    # Use subprocess popen to run command
                    # connect to STDIN and STDOUT
                    # run with path prepended
                    proc = Popen("(cd " + path + " && " + cmd + ")", shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
                    cmdout = path + ";" + proc.stdout.read()
                    cmdout = cmdout.replace("siren", "")
                    cmdout = cmdout.replace("\nsiren", "")
                    cmdout = cmdout.replace("siren\n", "")
                    self.conn.send(cmdout)
            except socket.timeout:
                print("SIREN connection has timed out")
                return
            except KeyboardInterrupt:
                sys.exit(0)

    def stop(self):
        self.conn.close()

# Listen on port 23
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
        sys.exit(0)

