#############################################################
# NAME: C1C Braden J Laverick                               #
# PROJECT: SIREN Project                                    #
# FILE: SIREN Logging Facility - db.py                      #
# DESCRIPTION:                                              #
# This file defines the master/starter class for the SIREN  #
# text and MySQL logging facility                           #
#############################################################

import threading, MySQLdb, sys, json, urllib2, ConfigParser


class logger_store(threading.Thread):

    def __init__(self, buffer, mutex):
        threading.Thread.__init__(self)
        self.buffer = buffer
        self.mutex = mutex
        config = ConfigParser.ConfigParser()
        config.read('siren.cfg')
        self.db = MySQLdb.connect(host=config.get('MySQL','host'),
                                  user=config.get('MySQL','user'),
                                  passwd=config.get('MySQL', 'password'),
                                  db=config.get('MySQL', 'database'))
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
                    args = data.split(';')
                    # generate unique ids
                    if args[0] == "SESSION":
                        georaw = urllib2.urlopen("http://atlas.dlinkddns.com/{}".format(args[3]))
                        geojson = json.load(georaw)
                        with open('log/log.txt', mode='a') as f:
                            f.write("{}: Client connected from address {}\n".format(args[1], args[3]))
                        self.cursor.execute("insert into SESSION values(NULL,'{}','{}','{}','{}','{}',{},{});".format(args[1], args[2], args[3], args[4], args[5], args[6], args[7]))
                        self.cursor.execute("select session_id from SESSION where source_ip='{}'".format(args[3]))
                        id = self.cursor.fetchone()[0]
                        row = self.cursor.fetchone()
                        while row is not None:
                            row = self.cursor.fetchone()
                        self.cursor.execute("insert into GEO values(NULL,'{}','{}','{}','{}','{}','{}',{},{}".format(id, geojson["country_code"], geojson["country_name"], geojson["region_code"], geojson["region_name"], geojson["city"], geojson["latitude"], geojson["longitude"]))
                    if args[0] == "UPDATE":
                        with open('log/log.txt', mode='a') as f:
                            f.write("Client closed connection at time {}\n".format(args[1]))
                        self.cursor.execute("update SESSION set endtime='{}' where starttime='{}';".format(args[1], args[2]))
                    if args[0] == "INPUT":
                        with open('log/log.txt', mode='a') as f:
                            f.write("{}: {} entered command: {}\n".format(args[2], args[1], args[3]))
                        self.cursor.execute("select session_id from SESSION where starttime='{}';".format(args[1]))
                        id = self.cursor.fetchone()[0]
                        row = self.cursor.fetchone()
                        while row is not None:
                            row = self.cursor.fetchone()
                        self.cursor.execute("insert into INPUT values(NULL,{},'{}','{}')".format(id,args[2],args[3]))
                    if args[0] == "AUTH":
                        self.cursor.execute("select session_id from SESSION where starttime='{}';".format(args[1]))
                        id = self.cursor.fetchone()[0]
                        row = self.cursor.fetchone()
                        while row is not None:
                            row = self.cursor.fetchone()
                        self.cursor.execute("insert into AUTH values(NULL,{},{},'{}','{}','{}')".format(id,args[2],args[3],args[4],args[5]))

                    self.db.commit()
                except KeyboardInterrupt:
                    print("Closing MySQL connection...")

    def stop(self):
        self.cursor.close()
        sys.exit(0)