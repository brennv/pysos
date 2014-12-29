import sys, pysosutils, os
from colors import *
from rhevlcbridge import Database, Cluster, Table, Host, StorageDomain

class rhevm():

    def __init__(self, target, db=False):
        self.target = target
        self.db = db

    def getRhevmVer(self):
        return pysosutils.getRpmVer(self.target, 'rhevm')

    def getReportsVer(self):
        return pysosutils.getRpmVer(self.target, 'rhevm-reports')

    def getDwhVer(self):
        return pysosutils.getRpmVer(self.target, 'rhevm-dwh')

    def _rhevmSimpleVer(self):
        rhevm = self.getRhevmVer()
        if "3.0" in rhevm:
            simpleVer = "3.0"
        elif "3.1" in rhevm:
            simpleVer = "3.1"
        elif "3.2" in rhevm:
            simpleVer = "3.2"
        elif "3.3" in rhevm:
            simpleVer = "3.3"
        elif "3.4" in rhevm:
            simpleVer = "3.4"
        else:
            simpleVer = "Could not be found"
        return simpleVer

    def checkForDb(self):
        fullPath = os.path.abspath(self.target)
        lcRoot = os.path.dirname(fullPath)

        if os.path.isdir(lcRoot + "/database"):
            return lcRoot + "/database"
        else:
            return False

    def parseDb(self):
        db = self.checkForDb()
        simpleVer = self._rhevmSimpleVer()
        if db:
            if simpleVer == "3.1" or simpleVer == "3.2" or simpleVer == "3.3" or simpleVer == "3.4":
                self.displayDbEval(db, simpleVer)
            elif simpleVer == "3.0":
                print colors.WARN + "\t Not ready to parse 3.0 databases yet, may not be trustworthy!!" + colors.ENDC
            else:
                print colors.WARN + "\t Database version needed for proper analysis" + colors.ENDC
        else:
            print colors.WARN + "Database not found" + colors.ENDC


    def parseEngineLog(self):
        logFile = open(self.target + 'var/log/ovirt-engine/engine.log', 'r')
        # Find most recent error line
        lines = logFile.readlines()
        errorLines = []
        for line in lines:
            if "ERROR" in line:

                errorLines.append(line)
        print ''

        for x in range(1,4):
            try:
                lastLine = len(errorLines)-x
                errorLine = errorLines[lastLine]
                errorProperties = errorLine.split(" ")
                '''
                0 - Date
                1 - Time
                3 - Command run
                7+ - Message
                '''

                print colors.BHEADER + "\t Time Stamp: " + colors.ENDC + errorProperties[0] + " " + errorProperties[1]
                print colors.BHEADER + "\t Command: " + colors.ENDC + errorProperties[3].lstrip("[").rstrip("]")

                # Trying to hack this since messages seem to vary in length - basing on last capital letter. deal with it
                errMessParts =  errorProperties[7:]
                errorMessage = ""
                for p in errMessParts:
                    #print p
                    for c in p:
                        if c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
                            #print errMessParts.index(p)
                            index = errMessParts.index(p)
                            errorMessage = ' '.join(errMessParts[index:]).replace("\n","")
                            #print errorMessage

                print colors.BHEADER + "\t Message: " + colors.ENDC  + errorMessage

                singleOccurance = True
                occurances = 0
                for line in lines:
                    if ' '.join(errorProperties[7:]) in line:
                        occurances += 1
                if occurances > 1:
                    singleOccurance = False

                if singleOccurance:
                    print colors.BHEADER + "\t Only occurance of this error: " + colors.WHITE + "Yes" + colors.ENDC
                else:
                    print colors.BHEADER + "\t Only occurance of this error: " + colors.ENDC + colors.RED + "No. Errors appear " + str(occurances) + " times in engine.log starting at " + ' '.join(errorLines[0].split(" ")[0:2]) + colors.ENDC

                print ""

            except:
                pass
        logFile.close()


    def displayRhevmInfo(self):
        print colors.BBLUE + '\t\t This is a RHEV Manager' + colors.ENDC
        print ''
        print colors.BHEADER + '\t RHEV-M Version : ' + colors.CYAN + self.getRhevmVer() + colors.ENDC
        print colors.BHEADER + '\t RHEV-M Reports : ' + colors.CYAN + self.getReportsVer() + colors.ENDC
        print colors.BHEADER + '\t RHEV-M DWH     : ' + colors.CYAN + self.getDwhVer() + colors.ENDC
        print ''
        dbPresent = self.checkForDb()
        if dbPresent:
            print colors.BLUE + '\t Database found. Can parse.' + colors.ENDC
        else:
            print colors.RED + '\t Database not found. Unable to parse.' + colors.ENDC

        print ''
        print '\t Most recent errors in engine.log : '
        self.parseEngineLog()
        
        if self.db:
            self.parseDb()

    def getMasterDbObj(self):
        dbTar = self.checkForDb() + "/sos_pgdump.tar"
        simpleVer = self._rhevmSimpleVer()
        masterDB = Database(dbTar, simpleVer)
        return masterDB

    def getDcList(self):
        masterDB = self.getMasterDbObj()
        return masterDB.get_data_centers()


    def getClusterList(self):
        masterDB = self.getMasterDbObj()
        return masterDB.get_clusters()

    def displayRhevDcInfo(self):
        masterDB = self.getMasterDbObj()
        # create DC list
        dcList = self.getDcList()
        print ""
        print colors.BSECTION + "RHEV Database Information" + colors.ENDC
        print ""
        print '\n\t' + colors.BOLD + colors.GREEN + '[Data Centers Managed By RHEV-M]' + colors.ENDC
        dc_table = Table(dcList,"name","uuid","compat")
        dc_table.display()
        
    def displayRhevStorageInfo(self):
        masterDB = self.getMasterDbObj()
        print '\n\t' + colors.BOLD + colors.GREEN + '[Storage Domains In All Data Centers]' + colors.ENDC
        sd_list = masterDB.get_storage_domains()
        sd_list.sort(key=lambda x: x.storage_type)
        sd_table = Table(sd_list,"name","uuid","storage_type","master")
        sd_table.display()
    
    def displayRhevClusterInfo(self):
        masterDB = self.getMasterDbObj()
        print '\n\t' + colors.BOLD + colors.GREEN + '[Clusters In All Data Centers]' + colors.ENDC
        clusterList = self.getClusterList()
        clusterList.sort(key=lambda x: x.dc_uuid)
        cluster_table = Table(clusterList, "name", "uuid", "compat_ver","cpu_type","dc_uuid")
        cluster_table.display()

    def displayRhevHyperInfo(self):
        dbDir = self.checkForDb()
        dcList = self.getDcList()
        clusterList = self.getClusterList()
        masterDB = self.getMasterDbObj()
        host_list = masterDB.get_hosts()
        hostDirs = []
        hostNameLen = 5
        # look for all files in the parent of the passed 'dbDir', and if it is a dir then attempts to parse
        rootDir = os.path.dirname(dbDir)
        for d in os.listdir(rootDir):
            if os.path.isdir(rootDir+"/"+d):
                hostDirs.append(d)
        # creating list of hosts without sosreports
        missingHostNames = []
        host_list.sort(key=lambda x: x.name)
        for h in host_list:
            for d in dcList:
                if h.get_uuid() == d.get_spm_uuid():
                    h.set_spm_status(True)
                else:
                    h.set_spm_status(False)
            for c in clusterList:
                if c.get_uuid() == h.get_host_dc_uuid():
                    for d in dcList:
                        if c.get_dc_uuid() == d.get_uuid():
                            h.set_host_dc_name(d.get_name())
            # try and find release version
            hostDirName = h.get_name().split(".")
            for dir in hostDirs:
                names = dir.split("-")
                # found a bug where all sosreport folders were lowercase but hostDirName was uppercase
                if names[0] == hostDirName[0].lower():
                    # this is a stupid hack, using '..' in the path name. stop being lazy and find a better alternative
                    releaseFile = open(dbDir+"/../"+dir+"/etc/redhat-release")
                    releaseVer = releaseFile.readlines()
                    if "Hypervisor" in releaseVer[0]:
                        host_release = releaseVer[0].split("(")[1]
                        # strip the newline character at the end of the line
                        host_release = host_release.replace("\n","")
                        host_release = host_release.rstrip(")")
                        h.set_release_ver(host_release)
                    else:
                        host_release = releaseVer[0].split()[6]
                        h.set_release_ver(host_release)
                    h.set_selinux(pysosutils.getSeLinux(dbDir+"/../"+dir+'/')['current'])
                else:
                    pass
        print '\n\t' + colors.BOLD + colors.GREEN + '[Hypervisors In All Data Centers]' + colors.ENDC
        host_table = Table(host_list,"name","uuid","host_dc_name","type", "spm", "selinux")
        host_table.display()        

        print '\n\t' + colors.BOLD + colors.GREEN + '[RPM Versions on All Hypervisors]' + colors.ENDC
        host_ver_table = Table(host_list, "name", "host_os", "vdsm_ver", "kvm_ver", "spice_ver", "kernel_ver")
        host_ver_table.display()

    def displayDbEval(self, db, simpleVer):
        self.displayRhevDcInfo()
        self.displayRhevClusterInfo()
        self.displayRhevStorageInfo()
        self.displayRhevHyperInfo()


if __name__ == '__main__':
    target = sys.argv[1]
    test = rhevm(target)
    test.displayRhevmInfo()
