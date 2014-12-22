import sys, os, re, opsys, pysosutils
from colors import *

class bios:

    def __init__(self, target):
        self.target = target
        if os.path.isfile(self.target+'dmidecode'):
            self.dmifile = self.target+'dmidecode'
        else:
            print 'No dmidecode file present'
            return False
    
    def getDimmInfo(self):
        dimmInfo = dict.fromkeys(['maxMem', 'dimmCount', 'emptyDimms', 'totalMem', 'memArrays'], 0)
        with open(self.dmifile, 'r') as dfile:
        # main iterables that have distinct leading names
            for line in dfile:
                if 'Maximum Capacity:' in line:
                    index = line.find(':')
                    dimmInfo['maxMem'] = line[index+1:len(line)].strip()
                if 'Number Of Devices:' in line:
                    dimmInfo['dimmCount'] += int(line.split()[3])
                if re.match('\tSize:', line):
                    if 'No Module Installed' in line:
                        dimmInfo['emptyDimms'] += 1
                    else:
                        size = int(line.split()[1])
                        dimmInfo['totalMem'] += size
                if 'Physical Memory Array' in line:
                    dimmInfo['memArrays'] +=  1
        return dimmInfo
                            
    def parseDmi(self, to_check):
        # Parse the given dmidecode file and then parse out the section specified by 'to_check'.
        # The results are then returned as a dictionary 
        return pysosutils.parseOutputSection(self.target+ 'sos_commands/hardware/dmidecode', to_check)

    def getBiosInfo(self):
        return self.parseDmi('BIOS Information')

    def getSysInfo(self):
        return self.parseDmi('System Information')
        
    def getProcInfo(self):
        proc = opsys.opsys(target=self.target)
        return proc.getCpuInfo()
        
    def displayBiosInfo(self):
        biosInfo = self.getBiosInfo()
        sysInfo = self.getSysInfo()
        procInfo = self.getProcInfo()
        dimmInfo = self.getDimmInfo()
        print colors.SECTION + colors.BOLD + 'DMI Decode' + colors.ENDC
        print '\t' + colors.HEADER_BOLD + 'BIOS' + colors.ENDC
        print '\t\t' + colors.BLUE + 'Vendor  : ' + colors.ENDC + biosInfo['Vendor']
        print '\t\t' + colors.BLUE + 'Version : ' + colors.ENDC + biosInfo['Version']
        print '\t\t' + colors.BLUE + 'Release : ' + colors.ENDC + biosInfo['Release Date']
        
        print '\t' + colors.HEADER_BOLD + 'System' + colors.ENDC
        print '\t\t' + colors.BLUE + 'Vendor  : ' + colors.ENDC + sysInfo['Manufacturer']
        print '\t\t' + colors.BLUE + 'Server  : ' + colors.ENDC + sysInfo['Product Name']
        print '\t\t' + colors.BLUE + 'Serial  : ' + colors.ENDC + sysInfo['Serial Number']
        print '\t\t' + colors.BLUE + 'UUID    : ' + colors.ENDC + sysInfo['UUID']
        
        print '\t' + colors.HEADER_BOLD + 'CPU' + colors.ENDC
        if procInfo['sockets'] > 0:
            print '\t\t' + colors.WHITE + '{} CPU sockets populated, {} cores / {} threads per core'.format(procInfo['sockets'], procInfo['cores'], procInfo['threadsPerCore']) + colors.ENDC
            print '\t\t' + colors.WHITE + '{} total physical cores - {} total threads'.format(procInfo['cores'], procInfo['processors']) + colors.ENDC
        else:
            print colors.WHITE + '\t\tThis is a Virtual Machine with no defined sockets, cores or threads' + colors.ENDC
        print '\t\t' + colors.BLUE + 'Family  : ' + colors.ENDC + procInfo['vendor'] + ' ' + procInfo['family']
        print '\t\t' + colors.BLUE + 'Model   : ' + colors.ENDC + procInfo['model']
        
        print '\t' + colors.HEADER_BOLD + 'Memory' + colors.ENDC
        print '\t\t' + colors.WHITE + '{} of {} DIMMs populated'.format((dimmInfo['dimmCount'] - dimmInfo['emptyDimms']), dimmInfo['dimmCount']) + colors.ENDC
        print '\t\t' + colors.BLUE + 'Total   : ' + colors.ENDC + str(dimmInfo['totalMem']) + ' MB' + '  ({} GB)'.format((dimmInfo['totalMem'] / 1024))
        print '\t\t' + colors.BLUE + 'Max Mem : ' + colors.ENDC + dimmInfo['maxMem']
        print '\t\t' + colors.GREEN + '{} total memory controllers, {} maximum per controller'.format(dimmInfo['memArrays'], dimmInfo['maxMem']) + colors.ENDC 
        
if __name__ == '__main__':
    target = sys.argv[1]
    test = bios(target=target)
    test.displayBiosInfo()

