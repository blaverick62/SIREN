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
import netifaces as ni
from time import sleep

import base64, datetime, threading, socket, traceback, sys, paramiko, ConfigParser
from paramiko.py3compat import u


class SSHInterface(paramiko.ServerInterface):
# Class that overrides some paramiko methods for the server
# provides tools to the control and handler threads for SSH
# Intricacies of SSH are handled here

    def __init__(self, pubkey, starttime):
        self.hostkey = paramiko.RSAKey(filename='sirenprivate.key')
        self.pubkey = paramiko.RSAKey(data=base64.b64decode(pubkey[7:]))
        self.event = threading.Event()
        self.starttime = starttime
        try:
            # Logging socket needed to catch authorization
            self.logsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.logsock.connect(('127.0.0.1', 1338))
        except Exception as e:
            print("Failed to connect to logging facility in paramiko server: " + str(e))
            traceback.print_exc()
            sys.exit(1)

    def check_channel_request(self, kind, chanid):
        # Open a Paramiko channel
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED



    def check_auth_password(self, username, password):
        # Override authorization with password to include logging
        with open('docs/users.txt', mode='r') as users:
            for line in users:
                auth = line.split(':')
                if username == auth[0] and password == auth[1]:
                    self.logsock.send("AUTH;{};{};{};{};{}".format(self.starttime, 1, username, password,
                                                                   datetime.datetime.now().strftime(
                                                                       '%Y-%m-%d %H:%M:%S')))
                    self.username = username
                    return paramiko.AUTH_SUCCESSFUL
            self.logsock.send("AUTH;{};{};{};{};{}".format(self.starttime, 1, username, password,
                                                           datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            return paramiko.AUTH_FAILED

    def check_auth_publickey(self, username, key):
        # Log username and public keys used
        print('Auth attempt with key: ' + u(hexlify(key.get_fingerprint())))
        with open('docs/users.txt', mode='r') as users:
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
        # Use GSS API
        if gss_authenticated == paramiko.AUTH_SUCCESSFUL:
            return paramiko.AUTH_SUCCESSFUL
        return paramiko.AUTH_FAILED

    def check_auth_gssapi_keyex(self, username,
                                gss_authenticated=paramiko.AUTH_FAILED,
                                cc_file=None):
        # Use GSS API
        if gss_authenticated == paramiko.AUTH_SUCCESSFUL:
            return paramiko.AUTH_SUCCESSFUL
        return paramiko.AUTH_FAILED

    def enable_auth_gssapi(self):
        UseGSSAPI = True
        GSSAPICleanupCredentials = False
        return UseGSSAPI

    def get_allowed_auths(self, username):
        # Define allowed authorizations
        return 'gssapi-keyex,gssapi-with-mic,password,publickey'

    def check_channel_shell_request(self, channel):
        # Tell the client that they have been given shell
        self.event.set()
        print("SHELL REQUESTED")
        return True

    def check_channel_pty_request(self, channel, term, width, height, pixelwidth, pixelheight,
                                  modes):
        # Give client a pseudo-terminal on request
        return True

    def check_channel_exec_request(self, channel, command):
        print(command)
        # Allow client to execute single commands, print them
        self.event.set()
        return True


class ssh_thread(threading.Thread):
# Handler thread class for SSH server
# Spawned on connection from client
# Spawns SSH Interface object

    def __init__(self, (client, addr), linaddr, pubkey, iface, detuser, index):
        threading.Thread.__init__(self)
        self.linsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.logsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client = client
        self.addr = addr
        self.pubkey = pubkey
        self.iface = iface
        self.detaddrs = linaddr
        self.detusers = detuser
        self.detsel = index
        paramiko.util.log_to_file('sirenssh.log')
        try:
            self.logsock.connect(('127.0.0.1', 1338))
        except socket.error as e:
            print("Failed to connect to logging facility" + str(e))
            traceback.print_exc()
            sys.exit(1)
        try:
            self.linsock.connect((self.detaddrs[self.detsel], 23))
        except socket.error:
            print("Failed to connect to detonation chamber")
            sys.exit(1)

    def run(self):
        tty = "S"
        hist = [[self.detsel, "S"]]
        # Allow GSS API and log start time of session
        DoGSSAPIKeyExchange = True
        self.starttime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Construct SSH server interface with respective key and start time
        # Start time needed to connect auths to appropriate session
        sshServer = SSHInterface(self.pubkey, self.starttime)
        try:
            # Instantiate paramiko transport layer
            t = paramiko.Transport(self.client, gss_kex=DoGSSAPIKeyExchange)
            t.set_gss_host(socket.getfqdn(""))
            try:
                t.load_server_moduli()
            except:
                print("Failed to load moduli: gex will be unsupported")
                raise
            # Add key to known hosts
            t.add_server_key(sshServer.hostkey)
            try:
                t.start_server(server=sshServer)
            except paramiko.SSHException:
                print('SSH negotiation failed.')
                sys.exit(1)

            # Get local ip with netifaces module and specified listening interface
            self.destip = ni.ifaddresses(self.iface)[2][0]['addr']
            # Get remote ip from transport layer
            ip = t.getpeername()[0]
            remoteport = self.addr[1]
            self.endtime = self.starttime
            # Now that all components are accounted for, log session
            self.logsock.send(
                "SESSION;{};{};{};{};{};{};{}".format(self.starttime, self.endtime, ip, self.destip, 'ssh', 22,
                                                      remoteport))
            print(ip)
            # Accept connection and open channel
            # Channel is analogous to paramiko socket
            self.chan = t.accept()

            if self.chan is None:
                print("No channel")
                sys.exit(1)

            sshServer.event.wait(10)
            if not sshServer.event.is_set():
                print('*** Client never asked for a shell.')
                sys.exit(1)

            # Send false welcome message and working directory
            self.linsock.send('siversion')
            ver = self.linsock.recv(256)
            if ver == "L":
                with open('docs/linuxintro.txt', mode='r') as f:
                    intro = f.read()
            else:
                with open('docs/windowsintro.txt', mode='r') as f:
                    intro = f.read()
            intro = intro.replace('\n', '\r\n')
            self.chan.send(intro + '\r\n')
            if ver == "L":
                self.linsock.send('pwd')
            else:
                self.linsock.send('cd .')
            response = self.linsock.recv(256)
            resplist = response.split(";")
            path = resplist[0][1]
            # Sanitize response from chamber to replace chamber username with SIREN username

            path = path.replace(self.detusers[self.detsel], sshServer.username)
            while True:
                # Replace home directory with ~
                path = path.replace("/home/" + sshServer.username, "~")
                # Send real-looking SSH prompt
                if ver == "L" and tty == "S":
                    self.chan.send(sshServer.username + '@ubuntu:' + path + '$ ')
                else:
                    self.chan.send(path + '>')
                data = ""

                # Wait for receive ready flag
                # Flag pops when at least one byte is ready for receive
                # Usually receive one byte at a time
                while self.chan.recv_ready() == False:
                    pass
                # Build input string until enter character is found
                while '\r' not in data:
                    rec = self.chan.recv(256)
                    if rec == '\b':
                        data = data[:-1]
                    else:
                        data = data + rec
                    self.chan.send(rec)
                self.chan.send('\n')
                # Cut off carriage return character
                data = data[:-1]
                if data == "exit":
                    # End sockets and log end time
                    if len(hist) > 1:
                        tty = hist[-1][1]
                        sel = hist[-1][0]
                        self.detsel = sel
                        self.linsock.send("TERMINATE")
                        self.linsock.close()
                        # Change detonation socket to new address
                        self.linsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        self.linsock.connect((self.detaddrs[self.detsel], 23))
                        self.linsock.send('siversion')
                        ver = self.linsock.recv(256)
                        if ver == "L":
                            self.linsock.send('pwd')
                        else:
                            self.linsock.send('cd .')
                        response = self.linsock.recv(256)
                        resplist = response.split(";")
                        path = resplist[0]
                    else:
                        self.endtime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        self.logsock.send("UPDATE;{};{}".format(self.endtime, self.starttime))
                        sleep(1)
                        self.linsock.send("TERMINATE")
                        self.logsock.send("TERMINATE")
                        self.chan.close()
                        sys.exit(0)
                timestmp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                # Detect SSH pivots to other machines
                if data[:3] == "ssh":
                    datarray = data.split()
                    self.logsock.send("INPUT;{};{};{}".format(self.starttime, timestmp, data))
                    # Parse into username and IP address of target
                    try:
                        addrarray = datarray[1].split("@")
                        sshaddr = addrarray[1]
                        sshuser = addrarray[0]
                        sel = -1
                        # Check if target is in the network
                        for ind in range(len(self.detaddrs)):
                            if sshaddr == self.detaddrs[ind]:
                                sel = ind
                        if sel != -1:
                            # If in network, start new thread with connection to new detonation chamber
                            success = 0
                            tries = 0
                            with open('docs/users.txt') as f:
                                while success == 0 and tries < 3:
                                    if tries > 0:
                                        self.chan.send("Permission denied, please try again.\r\n" + sshuser + "@" + sshaddr + "'s password: ")
                                    else:
                                        self.chan.send(sshuser + "@" + sshaddr + "'s password: ")
                                    passw = ""
                                    while self.chan.recv_ready() == False:
                                        pass
                                    # Build input string until enter character is found
                                    while '\r' not in passw:
                                        rec = self.chan.recv(256)
                                        if rec == '\b':
                                            passw = passw[:-1]
                                        else:
                                            passw = passw + rec
                                    self.chan.send('\n')
                                    # Cut off carriage return character
                                    passw = passw[:-1]
                                    for line in f:
                                        user = line.split(':')
                                        if user[0] == sshuser and user[1] == passw:
                                            success = 1
                                            break
                                    self.logsock.send(
                                        "AUTH;{};{};{};{};{}".format(self.starttime, success, sshuser, passw,
                                                                     datetime.datetime.now().strftime(
                                                                         '%Y-%m-%d %H:%M:%S')))
                                    tries += 1
                            if success == 0:
                                self.chan.send("Permission denied (publickey,password).\r\n")
                                continue
                            hist.append([sel, "S"])
                            self.detsel = sel
                            self.linsock.send("TERMINATE")
                            self.linsock.close()
                            # Change detonation socket to new address
                            tty = "S"
                            self.linsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            self.linsock.connect((self.detaddrs[self.detsel], 23))
                            self.linsock.send('siversion')
                            ver = self.linsock.recv(256)
                            if ver == "L":
                                with open('docs/linuxintro.txt', mode='r') as f:
                                    intro = f.read()
                            else:
                                with open('docs/windowsintro.txt', mode='r') as f:
                                    intro = f.read()
                            intro = intro.replace('\n', '\r\n')
                            self.chan.send(intro + '\r\n')
                            if ver == "L":
                                self.linsock.send('pwd')
                            else:
                                self.linsock.send('cd .')
                            response = self.linsock.recv(256)
                            resplist = response.split(";")
                            path = resplist[0]
                            # Sanitize response from chamber to replace chamber username with SIREN username

                            path = path.replace(self.detusers[self.detsel], sshServer.username)
                        else:
                            # If not, sleep and send back error
                            sleep(30)
                            self.chan.send("ssh: connect to host " + sshaddr + " port 22: Connection refused\r\n")
                            continue
                    except IndexError:
                        # If string cannot be parsed, send usage error
                        self.chan.send("usage: ssh [-1246AaCfGgKkMNnqsTtVvXxYy] [-b bind_address] [-c cipher_spec]\r\n\t[-D [bind_address:]port] [-E log_file] [-e escape_char]\r\n\t[-F configfile] [-I pkcs11] [-i identity_file] [-L address]\r\n\t[-l login_name] [-m mac_spec] [-O ctl_cmd] [-o option] [-p port]\r\n\t[-Q query_option] [-R address] [-S ctl_path] [-W host:port]\r\n\t[-w local_tun[:remote_tun]] [user@]hostname [command]\r\n")
                        continue

                elif data[:6] == "telnet":
                    datarray = data.split()
                    self.logsock.send("INPUT;{};{};{}".format(self.starttime, timestmp, data))
                    # Parse into username and IP address of target
                    try:
                        teladdr = data[1]
                        self.chan.send("Trying " + teladdr + "...")
                        sel = -1
                        # Check if target is in the network
                        for ind in range(len(self.detaddrs)):
                            if teladdr == self.detaddrs[ind]:
                               sel = ind
                            if sel != -1:
                               # If in network, start new thread with connection to new detonation chamber
                                success = 0
                                tries = 0
                                with open('docs/users.txt') as f:
                                    while success == 0 and tries < 3:
                                        self.chan.send("login: ")
                                        teluser = ""
                                        while self.chan.recv_ready() == False:
                                            pass
                                        # Build input string until enter character is found
                                        while '\r' not in teluser:
                                            rec = self.chan.recv(256)
                                            if rec == '\b':
                                                teluser = teluser[:-1]
                                            else:
                                                teluser = teluser + rec
                                        self.chan.send('\n')
                                        # Cut off carriage return character
                                        teluser = teluser[:-1]

                                        self.chan.send("password: ")
                                        passw = ""
                                        while self.chan.recv_ready() == False:
                                            pass
                                        # Build input string until enter character is found
                                        while '\r' not in passw:
                                            rec = self.chan.recv(256)
                                            if rec == '\b':
                                                passw = passw[:-1]
                                            else:
                                                passw = passw + rec
                                        self.chan.send('\n')
                                        # Cut off carriage return character
                                        passw = passw[:-1]

                                        for line in f:
                                            user = line.split(':')
                                            if user[0] == teluser and user[1] == passw:
                                                success = 1
                                                break
                                        self.logsock.send("AUTH;{};{};{};{};{}".format(self.starttime, success, teluser, passw, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
                                        tries += 1
                                if success == 0:
                                    self.chan.send("Unauthorized.\r\n")
                                    continue
                                hist.append([sel, "T"])
                                self.detsel = sel
                                self.linsock.send("TERMINATE")
                                self.linsock.close()
                                # Change detonation socket to new address
                                tty = "T"
                                self.linsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                                self.linsock.connect((self.detaddrs[self.detsel], 23))
                                self.linsock.send('siversion')
                                ver = self.linsock.recv(256)
                                if ver == "L":
                                    with open('docs/linuxintro.txt', mode='r') as f:
                                        intro = f.read()
                                else:
                                    with open('docs/windowsintro.txt', mode='r') as f:
                                        intro = f.read()
                                intro = intro.replace('\n', '\r\n')
                                self.chan.send(intro + '\r\n')
                                if ver == "L":
                                    self.linsock.send('pwd')
                                else:
                                    self.linsock.send('cd .')
                                response = self.linsock.recv(256)
                                resplist = response.split(";")
                                path = resplist[0]
                                # Sanitize response from chamber to replace chamber username with SIREN username

                                path = path.replace(self.detusers[self.detsel], sshServer.username)
                            else:
                                # If not, sleep and send back error
                                sleep(30)
                                self.chan.send("telnet: Unable to connect to remote host: Connection refused\r\n")
                                continue
                    except IndexError:
                        # If string cannot be parsed, send usage error
                        self.chan.send("telnet: Unable to connect to remote host: Connection refused\r\n")
                        continue
                # Check for evidence of SQL Injection, don't send to logger
                if "'" in data:
                    print("SQL Injection detected! Isolating threat...")
                    with open('threatlog.txt', mode='a') as threatlog:
                        threatlog.write(ip + ": " + data + '\n')
                else:
                    # Log input
                    self.logsock.send("INPUT;{};{};{}".format(self.starttime, timestmp, data))
                    # If sent command is netstat, send IP address as well
                    # Send command to the detonation chamber for processing
                    if data.split()[0] == "netstat":
                        self.linsock.sendall("netstat " + ip)
                    else:
                        self.linsock.sendall(data)
                    try:
                        response = self.linsock.recv(2048)
                    except socket.timeout as e:
                        print("Detonation chamber timed out: " + str(e))
                        traceback.print_exc()
                        sys.exit(1)
                    # Chamber sends back path;response, unpackage the message
                    resplist = response.split(";")
                    path = resplist[0]
                    # Sanitize path
                    path = path.replace(self.detusers[self.detsel], sshServer.username)
                    if resplist[1] != '':
                        # Sanitize response
                        chanresponse = '\r\n'.join(resplist[1].split('\n'))
                        chanresponse = chanresponse.replace('\n'+self.detusers[self.detsel], '\n' + sshServer.username)
                        chanresponse = chanresponse.replace(self.detusers[self.detsel]+'\n', sshServer.username + '\n')
                        chanresponse = chanresponse.replace(self.detusers[self.detsel], sshServer.username)
                        # Add clean carriage return/newline characters
                        if chanresponse[-2:] != "\r\n":
                            chanresponse = chanresponse + '\r\n'
                        self.chan.send(chanresponse)

        except Exception as e:
            print('SSH Caught exception: ' + str(e.__class__) + ': ' + str(e))
            traceback.print_exc()
            self.endtime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.logsock.send("UPDATE;{};{}".format(self.endtime, self.starttime))
            sleep(1)
            self.linsock.send("TERMINATE")
            self.logsock.send("TERMINATE")
            try:
                t.close()
            except:
                pass
            sys.exit(1)
        except KeyboardInterrupt:
            print("Keyboard interrupt caught in handler thread")
            self.logsock.send("UPDATE;{};{}".format(self.endtime, self.starttime))
            sleep(1)
            self.linsock.send("TERMINATE")
            self.logsock.send("TERMINATE")
            self.chan.close()
            sys.exit(0)

    def stop(self):
        self.chan.close()
        sys.exit(0)

        

class ssh_ctrl(threading.Thread):

    def __init__(self, pubkey):
        threading.Thread.__init__(self)
        self.pubkey = pubkey
        config = ConfigParser.ConfigParser()
        config.read('docs/siren.cfg')
        self.iface = config.get('Interfaces', 'interface')
        self.detaddrs = config.get('Detonation Chamber', 'host').split(',')
        self.detusers = config.get('Detonation Chamber', 'user').split(',')
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.sock.bind(('',22))
        except Exception as e:
            print("SSH bind failed " + str(e))
            traceback.print_exc()
            sys.exit(1)
        print("SSH server at " + ni.ifaddresses(self.iface)[2][0]['addr'])


    def run(self):
        self.threads = []
        try:
            while 1:
                try:
                    # Listen for connections
                    self.sock.listen(50)
                    newconn = self.sock.accept()
                    # Spawn handler thread and start it
                    th = ssh_thread(newconn, self.detaddrs, self.pubkey, self.iface, self.detusers, 0)
                    th.start()
                    # Append it to thread list
                    self.threads.append(th)
                except Exception as e:
                    print('SSH Listen/accept failed: ' + str(e))
                    traceback.print_exc()
                    for i in self.threads:
                        i.stop()
                    sys.exit(1)
        except KeyboardInterrupt:
            print("Keyboard interrupt caught in control thread")
            for i in self.threads:
                i.stop()
            sys.exit(0)

    def stop(self):
        for i in self.threads:
            i.stop()
        sys.exit(0)

        
