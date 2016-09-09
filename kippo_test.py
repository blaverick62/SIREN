############################################################
# NAME: C1C Braden J Laverick                              #
# PROJECT: HIVE Project                                    #
# FILE: Kippo Test File - kippo_test.py                    #
# DESCRIPTION:                                             #
# This file is a test run of the kippo API, it will be     #
# integrated into the HIVE Project after testing is        #
# complete.                                                #
#########################################################
import subprocess, os

currdir = os.getcwd()
os.chdir("kippo")
subprocess.call(['./pystart.sh'])
os.chdir("..")

