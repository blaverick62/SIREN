#############################################################
# NAME: C1C Braden J Laverick                               #
# PROJECT: SIREN Project                                    #
# FILE: SIREN Server Classes - telnet_server.py             #
# DESCRIPTION:                                              #
# This file specifies the classes for the various control   #
# servers that SIREN implements.                            #
#############################################################

import socket, threading

class telnetClientThread(threading.Thread):
    def __init__(self,(conn,addr)):
        self.conn=conn
        self.addr=addr
        print("Connected with SIREN control at %s..." % self.conn)
        threading.Thread.__init__(self)


    def run(self):

        while True:
            data = self.conn.recv(256)
            print(data)
            self.conn.send(b'Message received fam!\r\n')


telsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
telsock.bind(('', 23))
telsock.listen(5)
while 1:
    th = telnetClientThread(telsock.accept())
    th.start()
    pass
