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

from server.telnet_server import *
from server.ssh_server import *
from log.logger import *
from time import sleep
from os import chmod
from Crypto.PublicKey import RSA

import sys

def ipCheck(ip):
    iparr = ip.split('.')
    if len(iparr) != 4:
        return 0
    for n in iparr:
        if int(n) < 0 or int(n) > 255:
            return 0
    return 1

def main():
    with open('sirenpublic.key', mode='r') as content_file:
        pubkey = content_file.readline()

    iface = str(raw_input("What interface would you like to listen on? >> "))

    config = open("siren.config", mode='w')
    linaddr = '256.256.256.256'
    while ipCheck(linaddr) == 0:
        linaddr = str(raw_input("What is the IP address of the Linux Detonation Chamber? >> "))
        if ipCheck(linaddr) == 0:
            print("Invalid IP address. Please try again.")
    config.write(linaddr + '\n')
    #winaddr = str(raw_input("What is the IP address of the Windows Detonation Chamber? >> "))
    winaddr = '0.0.0.0'
    config.write(winaddr + '\n')
    config.close()

    dbAddr = '256.256.256.256'
    while ipCheck(dbAddr) == 0:
        dbAddr = str(raw_input("What is the IP address of the database? >> "))
        if ipCheck(dbAddr) == 0:
            print("Invalid IP address. Please try again.")

    siren_log = logger(dbAddr, 'sirenlocal', 'sirenproj')
    siren_log.setDaemon(True)
    siren_log.start()
    sleep(10)

    ssh_thread = ssh_ctrl(pubkey, iface)
    ssh_thread.setDaemon(True)

    telnet_thread = telnet_ctrl(iface)
    telnet_thread.setDaemon(True)



    try:
        ssh_thread.start()
        telnet_thread.start()
    except KeyboardInterrupt:
        ssh_thread.stop()
        telnet_thread.stop()
        sys.exit()

    try:
        while 1:
            try:
                line = sys.stdin.read()
                if line == "exit":
                    ssh_thread.stop()
                    telnet_thread.stop()
                    sys.exit(0)
            except Exception:
                ssh_thread.stop()
                telnet_thread.stop()
                sys.exit(0)
    except KeyboardInterrupt:
        print("Keyboard interrupt caught in main")
        ssh_thread.stop()
        siren_log.stop()
        sys.exit(0)


if __name__ == "__main__":
    main()

