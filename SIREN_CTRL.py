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

from server.http_server import *
from server.ftp_server import *
from server.telnet_server import *
from log.logger import *


import subprocess, sys, os, signal

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
    config = open("siren.config", mode='w')
    linaddr = str(raw_input("What is the IP address of the Linux Detonation Chamber? >> "))
    config.write(linaddr + '\n')
    #winaddr = str(raw_input("What is the IP address of the Windows Detonation Chamber? >> "))
    winaddr = '0.0.0.0'
    config.write(winaddr + '\n')
    config.close()

    username = str(raw_input("What is your username? > "))
    password = str(raw_input("What is your password? > "))

    siren_log = logger(username, password)
    siren_log.setDaemon(True)

    #http_thread = http_ctrl()
    #http_thread.setDaemon(True)

    #ftp_thread = ftp_ctrl()
    #ftp_thread.setDaemon(True)

    telnet_thread = telnet_ctrl()
    telnet_thread.setDaemon(True)





    try:
        pass
        #http_thread.start()
        #ftp_thread.start()
        siren_log.start()
        telnet_thread.start()
    except KeyboardInterrupt:
        #http_thread.stop()
        #ftp_thread.stop()
        telnet_thread.stop()
        sys.exit()


    while 1:
        try:
            leave = raw_input("Enter exit to quit >> ")
            if leave == "exit":
                telnet_thread.stop()
                sys.exit()
        except KeyboardInterrupt:
            #http_thread.stop()
            #ftp_thread.stop()
            telnet_thread.stop()
            break
        except Exception:
            telnet_thread.stop()



if __name__ == "__main__":
    main()

