#############################################################
# NAME: C1C Braden J Laverick                               #
# PROJECT: SIREN Project                                    #
# FILE: SIREN Logging Facility - db.py                      #
# DESCRIPTION:                                              #
# This file defines the master/starter class for the SIREN  #
# text and MySQL logging facility                           #
#############################################################

import threading, MySQLdb


class logger_store(threading.Thread):

    def __init__(self, buffer, mutex, username, password):
        threading.Thread.__init__(self)
        self.buffer = buffer
        self.mutex = mutex
        self.db = MySQLdb.connect(host="localhost",
                                  user=username,
                                  passwd=password,
                                  db="siren_db")
        self.cursor = self.db.cursor()
        for line in open("log/siren_schema.sql"):
            self.cursor.execute(line)

    def run(self):
        while(1):
            if(self.buffer.empty() == False):
                try:
                    self.mutex.acquire()
                    try:
                        data = self.buffer.get()
                    finally:
                        self.mutex.release()
                    print(data + " - From logger")
                    args = data.split(';')
                    if args[0] == "SESSION":
                        with open('log/log.txt', mode='a') as f:
                            f.write("{}: Client connected from address {}\n".format(args[1], args[2]))
                        self.cursor.execute("insert into SESSION values(NULL,'{}','{}');".format(args[1], args[2]))
                    if args[0] == "INPUT":
                        with open('log/log.txt', mode='a') as f:
                            f.write("{}: {} entered command: {}\n".format(args[2], args[1], args[3]))
                        id = self.cursor.execute("select session_id from SESSION where ip='{}';".format(args[1]))
                        self.cursor.execute("insert into INPUT values(NULL,{},'{}','{}')".format(id,args[2],args[3]))
                    self.db.commit()
                except KeyboardInterrupt:
                    print("Closing MySQL connection...")