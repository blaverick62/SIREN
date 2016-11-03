#############################################################
# NAME: C1C Braden J Laverick                               #
# PROJECT: SIREN Project                                    #
# FILE: SIREN Server Classes - base.py                      #
# DESCRIPTION:                                              #
# This file specifies the base attributes and methods for   #
# all SIREN servers.                                        #
#############################################################

import socket, threading, os, time, sys
from detonation.det_routes import *
from ftp_server import *
from http_server import *
from telnet_server import *

class base:

    def __init__(self, winDet, linDet):
        self.winDet = winDet
        self.linDet = linDet

    def start(self):

        self.http_thread = http_ctrl()
        self.http_thread.setDaemon(True)

        self.ftp_thread = ftp_ctrl()
        self.ftp_thread.setDaemon(True)

        self.telnet_thread = telnet_ctrl()
        self.telnet_thread.setDaemon(True)


        self.http_thread.start()
        self.ftp_thread.start()
        self.telnet_thread.start()

    def stop(self):

        self.http_thread.stop()
        self.ftp_thread.stop()
        self.telnet_thread.stop()
        self.winDet.det_close()
        self.linDet.det_close()
