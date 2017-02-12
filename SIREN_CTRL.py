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

import sys, ConfigParser

# Check validity of IP addresses
def ipCheck(ip):
    iparr = ip.split('.')
    if len(iparr) != 4:
        return 0
    for n in iparr:
        if int(n) < 0 or int(n) > 255:
            return 0
    return 1

def main():
    # Read in public key
    with open('sirenpublic.key', mode='r') as content_file:
        pubkey = content_file.readline()

    # Start logger
    siren_log = logger()
    #siren_log.setDaemon(True)
    siren_log.start()
    sleep(10)

    ssh_thread = ssh_ctrl(pubkey)
    #ssh_thread.setDaemon(True)

    telnet_thread = telnet_ctrl()
    #telnet_thread.setDaemon(True)


    # Start server threads\
    try:
        ssh_thread.start()
        telnet_thread.start()
    except KeyboardInterrupt:
        ssh_thread.stop()
        telnet_thread.stop()
        sys.exit()

    try:
        # Stdin catch doesn't work
        while 1:
            try:
                line = sys.stdin.read()
                if line == "exit":
                    ssh_thread.stop()
                    telnet_thread.stop()
                    siren_log.stop()
                    sys.exit(0)
            except Exception:
                ssh_thread.stop()
                telnet_thread.stop()
                siren_log.stop()
                sys.exit(0)
    # Catches interrupt, doesn't do anything
    except KeyboardInterrupt:
        print("Keyboard interrupt caught in main")
        ssh_thread.stop()
        telnet_thread.stop()
        siren_log.stop()
        sys.exit(0)


if __name__ == "__main__":
    main()

