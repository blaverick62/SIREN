#############################################################
# NAME: C1C Braden J Laverick                               #
# PROJECT: SIREN Project                                    #
# FILE: SIREN Server Classes - ssh_server.py                #
# DESCRIPTION:                                              #
# This file specifies the classes for the ssh control       #
# server that SIREN implements.                             #
# DOCUMENTATION: This server class is based off of the      #
# implementation found at https://github.com/paramiko/      #
# paramiko/blob/master/demos/demo_server.py                 #
#############################################################


from binascii import hexlify

import base64
import datetime
import threading
import socket
import traceback
import sys
import paramiko
from paramiko.py3compat import u


class SSHInterface(paramiko.ServerInterface):

    def __init__(self, pubkey, starttime):

        self.hostkey = paramiko.RSAKey(filename='/root/sirenprivate.key')
        self.pubkey = paramiko.RSAKey(data=base64.b64decode(pubkey[7:]))
        self.event = threading.Event()
        self.starttime = starttime
        try:
            self.logsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.logsock.connect(('127.0.0.1', 1337))
        except Exception as e:
            print("Failed to connect to logging facility in paramiko server: " + str(e))
            traceback.print_exc()
            sys.exit(1)

    def check_channel_request(self, kind, chanid):
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_auth_password(self, username, password):
        with open('server/users.txt', mode='r') as users:
            for line in users:
                auth = line.split(':')
                if username == auth[0] and password == auth[1]:
                    self.logsock.send("AUTH;{};{};{};{};{}".format(self.starttime, 1, username, password,
                                                                   datetime.datetime.now().strftime(
                                                                       '%Y-%m-%d %H:%M:%S')))
                    return paramiko.AUTH_SUCCESSFUL
            self.logsock.send("AUTH;{};{};{};{};{}".format(self.starttime, 1, username, password,
                                                           datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            return paramiko.AUTH_FAILED

    def check_auth_publickey(self, username, key):
        print('Auth attempt with key: ' + u(hexlify(key.get_fingerprint())))
        with open('server.users.txt', mode='r') as users:
            for line in users:
                auth = line.split(':')
                if username == auth[0] and key == self.pubkey:
                    self.logsock.send("AUTH;{};{};{};{};{}".format(self.starttime, 1, username, key,
                                                                   datetime.datetime.now().strftime(
                                                                       '%Y-%m-%d %H:%M:%S')))
                    return paramiko.AUTH_SUCCESSFUL
            self.logsock.send("AUTH;{};{};{};{};{}".format(self.starttime, 0, username, key,
                                                           datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            return paramiko.AUTH_FAILED

    def check_auth_gssapi_with_mic(self, username,
                                   gss_authenticated= paramiko.AUTH_FAILED,
                                   cc_file=None):
        if gss_authenticated == paramiko.AUTH_SUCCESSFUL:
            return paramiko.AUTH_SUCCESSFUL
        return paramiko.AUTH_FAILED

    def check_auth_gssapi_keyex(self, username,
                                gss_authenticated=paramiko.AUTH_FAILED,
                                cc_file=None):
        if gss_authenticated == paramiko.AUTH_SUCCESSFUL:
            return paramiko.AUTH_SUCCESSFUL
        return paramiko.AUTH_FAILED

    def enable_auth_gssapi(self):
        UseGSSAPI = True
        GSSAPICleanupCredentials = False
        return UseGSSAPI

    def get_allowed_auths(self, username):
        return 'gssapi-keyex,gssapi-with-mic,password,publickey'

    def check_channel_shell_request(self, channel):
        self.event.set()
        return True

    def check_channel_pty_request(self, channel, term, width, height, pixelwidth, pixelheight,
                                  modes):
        return True



class ssh_ctrl(threading.Thread):

    def __init__(self, pubkey):
        threading.Thread.__init__(self)
        self.pubkey = pubkey
        detaddrs = open("siren.config", mode="r")
        addrs = detaddrs.read()
        spaddrs = addrs.split('\n')
        linaddr = spaddrs[0]
        detaddrs.close()
        self.linsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.logsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # winconn = self.winsock.connect((winaddr, 23))
        try:
            self.logsock.connect(('127.0.0.1', 1338))
        except socket.error as e:
            print("Failed to connect to logging facility" + str(e))
            traceback.print_exc()
            sys.exit(1)
        try:
            self.linsock.connect((linaddr, 23))
        except socket.error:
            print("Failed to connect to detonation chamber")
            sys.exit(1)
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.sock.bind(('',22))
        except Exception as e:
            print("SSH bind failed " + str(e))
            traceback.print_exc()
            sys.exit(1)
        print("SSH server at " + socket.gethostbyname(socket.gethostname()))


    def run(self):
        try:
            self.sock.listen(50)
            client, addr = self.sock.accept()
            # Authorization and brute force logger
            self.starttime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.destip = socket.gethostbyname(socket.gethostname())
            ip = addr[0]
            remoteport = addr[1]
            self.endtime = self.starttime
            self.logsock.send(
                "SESSION;{};{};{};{};{};{}".format(self.starttime, self.endtime, ip, self.destip, 'ssh', 22,
                                                   remoteport))
            print(addr[0])
        except Exception as e:
            print('SSH Listen/accept failed: ' + str(e))
            traceback.print_exc()
            sys.exit(1)
        except KeyboardInterrupt:
            print("Keyboard interrupt caught")
            sys.exit(0)

        DoGSSAPIKeyExchange = True
        sshServer = SSHInterface(self.pubkey, self.starttime)
        try:
            t = paramiko.Transport(client, gss_kex=DoGSSAPIKeyExchange)
            t.set_gss_host(socket.getfqdn(""))
            try:
                t.load_server_moduli()
            except:
                print("Failed to load moduli: gex will be unsupported")
                raise
            t.add_server_key(sshServer.hostkey)
            try:
                t.start_server(server=sshServer)
            except paramiko.SSHException:
                print('SSH negotiation failed.')
                sys.exit(1)

            chan = t.accept()

            if chan is None:
                print("No channel")
                sys.exit(1)

            sshServer.event.wait(10)
            if not sshServer.event.is_set():
                print('*** Client never asked for a shell.')
                sys.exit(1)

            chan.settimeout(30)
            chan.send('\r\n\r\nWelcome to Ubuntu 16.04\r\n\r\n')
            self.linsock.send('pwd')
            response = self.linsock.recv(256)
            chan.send(response)
            while True:
                try:
                    data = chan.recv(256)
                except socket.timeout:
                    print("Attacker closed connection")
                    self.endtime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    self.logsock.send("UPDATE;{};{}".format(self.endtime, self.starttime))
                    continue
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
                    # self.winconn.sendall(data)


                    if data[:2] == 'cd':
                        self.linsock.sendall(data)


                    elif data[:3] == 'pwd':
                        self.linsock.sendall(data)
                        try:
                            response = self.linsock.recv(20000)
                        except socket.timeout:
                            print("Connection with detonation chamber has timed out")
                            self.endtime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                            self.logsock.send("UPDATE;{};{}".format(self.endtime, self.starttime))
                            return
                        chan.send(response)


                    elif data[:2] == 'ls':
                        self.linsock.sendall(data)
                        try:
                            response = self.linsock.recv(20000)
                        except socket.timeout:
                            print("Connection with detonation chamber has timed out")
                            self.endtime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                            self.logsock.send("UPDATE;{};{}".format(self.endtime, self.starttime))
                            self.linsock.close()
                            return
                        chan.send(response)


                    elif data[:5] == 'touch':
                        self.linsock.sendall(data)


                    elif data[:4] == 'echo':
                        self.linsock.sendall(data)
                        try:
                            response = self.linsock.recv(20000)
                        except socket.timeout:
                            print("Connection with detonation chamber has timed out")
                            self.endtime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                            self.logsock.send("UPDATE;{};{}".format(self.endtime, self.starttime))
                            return
                        chan.send(response)


                    else:
                        self.linsock.sendall("echo 'command not found'")
                        try:
                            response = self.linsock.recv(20000)
                        except socket.timeout:
                            print("Connection with detonation chamber has timed out")
                            self.endtime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                            self.logsock.send("UPDATE;{};{}".format(self.endtime, self.starttime))
                            return
                        chan.send(response)

        except Exception as e:
            print('SSH Caught exception: ' + str(e.__class__) + ': ' + str(e))
            traceback.print_exc()
            self.endtime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.logsock.send("UPDATE;{};{}".format(self.endtime, self.starttime))
            try:
                t.close()
            except:
                pass
            sys.exit(1)
