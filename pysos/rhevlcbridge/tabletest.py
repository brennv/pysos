'''
Created on Jan 3, 2014

@author: wallace
'''
from rhevlcbridge import *
import os

#dbFile = "/home/wallace/cases/00945926/LogCollector/database/sos_pgdump.tar"
dbFile = "/home/wallace/cases/01002915/sosreport-LogCollector-20131223183303/database/sos_pgdump.tar"
#dbFile = "/home/wallace/cases/00986768/sosreport-LogCollector-comp-wguo-20131120115048-5fd4/database/sos_pgdump.tar"

database = Database(dbFile)

#for f in dir(database):
#	print f

testHosts = database.get_hosts()
#print len(testHosts)

#this needs to be done because the 'pysos' utility sets SPM during a loop, it is not something that is set when the host class is initialized
spmHost = testHosts[0]
spmHost.set_spm_status("*")

print "TESTING table.py"
print ""
print "Creating 3 test tables..."
print ""
print "Testing with Table(testHosts,name,uuid,host_dc_name,spm_status)"
testTable = Table(testHosts,"name","spm_status","uuid","uuid")
print "-----------------------------"
print "Testing with Table (testHosts)"
testTable2 = Table(testHosts)
print "-----------------------------"
print "Testing with no data Table('name')"
testTable3 = Table("name")
print ""

print "Validating the tables..."
print "------------------------------"
if testTable.validate():
	print "TEST 1 PASSES!!!!!"
else:
	print "TEST 1 FAILED!!!!!"
print "------------------------------"
if testTable2.validate():
	print "TEST 2 PASSES!!!!!"
else:
	print "TEST 2 FAILED!!!!!"
print "------------------------------"
if testTable3.validate():
	print "TEST 3 PASSES!!!!!"
else:
	print "TEST 3 FAILED!!!!!"
	
print ""
print "Testing display function"
print ""
testTable.display()
print "------------------------------"
#testTable2.display()
# print "------------------------------"
# testTable3.display()
# print "------------------------------"
