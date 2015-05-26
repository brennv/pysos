import sys
import os
import re
import opsys
import pysosutils
from colors import Color as c

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
        self.pprint = c()

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
            self.pprint.bsection('DMI Decode')
            self.pprint.bheader('\tBIOS')
            self.pprint.blue('\t\tVendor  : ', biosInfo['Vendor'])
            self.pprint.blue('\t\tVersion : ', biosInfo['Version'])
            self.pprint.blue('\t\tRelease : ', biosInfo['Release Date'])
        else:
            self.pprint.bred('\t\t Could not parse dmidecode')

        if sysInfo:
            self.pprint.bheader('\tSystem')
            self.pprint.blue('\t\tVendor  : ', sysInfo['Manufacturer'])
            self.pprint.blue('\t\tServer  : ', sysInfo['Product Name'])
            self.pprint.blue('\t\tSerial  : ', sysInfo['Serial Number'])
            self.pprint.blue('\t\tUUID    : ', sysInfo['UUID'])

        self.pprint.bheader('\tCPU')

        if procInfo.sockets > 0:
            self.pprint.white(
                    '\t\t{} sockets - {} cores - {} threads per core'.format(
                        procInfo.sockets, procInfo.cores,
                        procInfo.threadspercore
                        )
                    )
            self.pprint.white('\t\t{} total cores {} total threads'.format(
                        procInfo.cores,
                        procInfo.processors
                        )
                    )
        else:
            self.pprint.white(
                '\t\tVirtual Machine with no defined sockets or cores'
            )
        self.pprint.blue('\t\tFamily  : ',
                procInfo.vendor,
                ' ',
                procInfo.family
            )
        self.pprint.blue('\t\tModel   : ', procInfo.model.strip())
        self.pprint.bheader('\tMemory')
        self.pprint.white('\t\t{} of {} DIMMs populated'.format(
                            (dimm.dimmCount - dimm.emptyDimms),
                            dimm.dimmCount
                            )
                        )
        self.pprint.blue('\t\tTotal   : ',
                        str(dimm.totalMem),
                        ' MB',
                        '  ({} GB)'.format(
                                (dimm.totalMem / 1024)
                            )
                        )
        self.pprint.blue('\t\tMax Mem : ',
                        '{} GB'.format(dimm.maxMem)
                        )
        self.pprint.green(
            '\t\t{} total controllers {} GB maximum per controller'.format(
                dimm.memArrays, dimm.maxMem
                )
            )

if __name__ == '__main__':
    target = sys.argv[1]
    test = bios(target=target)
    test.displayBiosInfo()
