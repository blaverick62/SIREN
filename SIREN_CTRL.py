#############################################################
# NAME: C1C Braden J Laverick                               #
# PROJECT: SIREN Project                                    #
# FILE: SIREN Control Module - SIREN_CTRL.py                #
# DESCRIPTION:                                              #
# This file is the control module for the SIREN project.    #
# The program will take in commands from the adversary on   #
# protocol listeners and route them to the appropriate VMs. #
# The module is also equipped with logging, data acqusition,#
# and can record data on the attacker.                      #
#############################################################

import threading
from server.base import base
from detonation import detChamber

import subprocess, sys, os, socket

# Clean up kippo exit
def knode_start():
    os.chdir('kippo')
    print("Starting Kippo Honeypot...")
    kipStart = "twistd -y kippo.tac -l log/kippo.log --pidfile kippo.pid"
    subprocess.Popen(kipStart.split())
    os.chdir('..')
    print("Kippo Running in Background...")

def knode_stop():
    os.chdir('kippo')
    subprocess.call(['./stop.sh'])
    os.chdir('..')

def main():

    linaddr = input("What is the IP address of the Linux Detonation Chamber? >> ")
    winaddr = input("What is the IP address of the Windows Detonation Chamber? >> ")

    linDet = detChamber(linaddr)
    winDet = detChamber(winaddr)

    siren_server = base(winDet, linDet)


    try:
        knode_start()
        siren_server.start()
    except KeyboardInterrupt:
        siren_server.start()
        #knode_stop()
        sys.exit()


    while 1:
        if sys.stdin == "exit":
            #http_thread.stop()
            #ftp_thread.stop()
            #telnet_thread.stop()
            #knode_stop()
            break


if __name__ == "__main__":
    main()

