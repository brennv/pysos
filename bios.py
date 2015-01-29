import sys
import os
import re
import opsys
import pysosutils
from colors import *

class Object(object):
    pass

class bios:
    """ Capture and optionally display bios and dmidecode data """

    def __init__(self, target):
        self.target = target
        if os.path.isfile(self.target+'dmidecode'):
            self.dmifile = self.target+'dmidecode'
        else:
            print 'No dmidecode file present'
            return False

    def getDimmInfo(self):
        """ Get information about populated and empty dimms.
        We can then also extract memory support data from this
        """
        props = ['maxMem', 'dimmCount', 'emptyDimms', 'totalMem',
                    'memArrays']
        dimm = Object()
        for prop in props:
            setattr(dimm, prop, int())
        with open(self.dmifile, 'r') as dfile:
        # main iterables that have distinct leading names
            for line in dfile:
                if 'Maximum Capacity:' in line:
                    index = line.find(':')
                    maxmem = line[index+1:len(line)].strip()
                    if 'GB' in maxmem:
                        dimm.maxMem = int(maxmem.strip('GB'))
                    elif 'TB' in maxmem:
                        dimm.maxMem = int(maxmem.strip('TB')) * 1024
                if 'Number Of Devices:' in line:
                    dimm.dimmCount += int(line.split()[3])
                if re.match('\tSize:', line):
                    if 'No Module Installed' in line:
                        dimm.emptyDimms += 1
                    else:
                        size = int(line.split()[1])
                        dimm.totalMem += size
                if 'Physical Memory Array' in line:
                    dimm.memArrays +=  1
        return dimm

    def parseDmi(self, to_check):
        """ 
        Parse the given dmidecode file and then parse out
        the section specified by the 'to_check' arg.

        The results are then returned as a dictionary
        """
        return pysosutils.parseOutputSection(self.target +
                            'sos_commands/hardware/dmidecode', to_check)

    def getBiosInfo(self):
        return self.parseDmi('BIOS Information')

    def getSysInfo(self):
        return self.parseDmi('System Information')

    def getProcInfo(self):
        """
        Call getCpuInfo() from opsys module to get processor data 
        """
        proc = opsys.opsys(target=self.target)
        return proc.getCpuInfo()

    def getAllBiosInfo(self):
        bios = Object()
        biosdmi = Object()
        sysdmi = Object()
        bios.dimm = self.getDimmInfo()
        biosDmiInfo = self.getBiosInfo()
        for key in biosDmiInfo:
            setattr(biosdmi, key.replace(" ", '').lower(), biosDmiInfo[key])
        bios.biosdmi = biosdmi
        sysDmiInfo = self.getSysInfo()
        for key in sysDmiInfo:
            setattr(sysdmi, key.replace(" ", '').lower(), sysDmiInfo[key])
        bios.sysdmi = sysdmi
        return bios

    def displayBiosInfo(self):
        """ Display bios and dmidecode related data """
        biosInfo = self.getBiosInfo()
        sysInfo = self.getSysInfo()
        procInfo = self.getProcInfo()
        dimm = self.getDimmInfo()
        if biosInfo:
            print colors.BSECTION + 'DMI Decode' + colors.ENDC
            print '\t' + colors.BHEADER + 'BIOS' + colors.ENDC
            print '\t\t' + colors.BLUE + 'Vendor  : ' + colors.ENDC\
                        + biosInfo['Vendor']
            print '\t\t' + colors.BLUE + 'Version : ' + colors.ENDC\
                        + biosInfo['Version']
            print '\t\t' + colors.BLUE + 'Release : ' + colors.ENDC\
                        + biosInfo['Release Date']
        else:
            print colors.BRED + '\t\t Could not parse dmidecode' + colors.ENDC
        if sysInfo:
            print '\t' + colors.BHEADER + 'System' + colors.ENDC
            print '\t\t' + colors.BLUE + 'Vendor  : ' + colors.ENDC\
                        + sysInfo['Manufacturer']
            print '\t\t' + colors.BLUE + 'Server  : ' + colors.ENDC\
                        + sysInfo['Product Name']
            print '\t\t' + colors.BLUE + 'Serial  : ' + colors.ENDC\
                        + sysInfo['Serial Number']
            print '\t\t' + colors.BLUE + 'UUID    : ' + colors.ENDC\
                        + sysInfo['UUID']

        print '\t' + colors.BHEADER + 'CPU' + colors.ENDC
        if procInfo.sockets > 0:
            print '\t\t' + colors.WHITE +\
            '{} sockets - {} cores - {} threads per core'.format(
                        procInfo.sockets, procInfo.cores,
                        procInfo.threadspercore) + colors.ENDC
            print '\t\t' + colors.WHITE + '{} total cores {} total threads'.format(
                        procInfo.cores,
                        procInfo.processors) + colors.ENDC
        else:
            print colors.WHITE +\
                '\t\tVirtual Machine with no defined sockets or cores'\
                + colors.ENDC
        print '\t\t' + colors.BLUE + 'Family  : ' + colors.ENDC\
                + procInfo.vendor + ' ' + procInfo.family
        print '\t\t' + colors.BLUE + 'Model   : ' + colors.ENDC\
                + procInfo.model.strip()

        print '\t' + colors.BHEADER + 'Memory' + colors.ENDC
        print '\t\t' + colors.WHITE + '{} of {} DIMMs populated'.format(
                (dimm.dimmCount - dimm.emptyDimms),
                dimm.dimmCount) + colors.ENDC
        print '\t\t' + colors.BLUE + 'Total   : ' + colors.ENDC + str(
                dimm.totalMem) + ' MB' + '  ({} GB)'.format((
                dimm.totalMem / 1024))
        print '\t\t' + colors.BLUE + 'Max Mem : ' + colors.ENDC\
                + '{} GB'.format(dimm.maxMem)
        print '\t\t' + colors.GREEN +\
        '{} total controllers {} GB maximum per controller'.format(
        dimm.memArrays, dimm.maxMem) + colors.ENDC 

if __name__ == '__main__':
    target = sys.argv[1]
    test = bios(target=target)
    test.displayBiosInfo()
