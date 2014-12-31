import sys
import os
import re
import math
import pysosutils
from colors import *

class Object(object):
    pass

class memory:
    """ Capture and optionally display memory related data """

    def __init__(self, target):
        self.target = target
        self.mem = self.getMemInfo()

    def _graph(self, perc):
        """ 
        General graphing function to spit out a line graph.

        Needs to be fed a percentage as th 'perc' arg.
        """
        tick = u"\u25C6"
        empty = u"\u25C7"
        if perc == 0:
            filled = 0
        else:
            filled = round(40 * (perc / 100))
        nofill = 40 - filled
        percf = '%.2f' %perc + ' %'
        graph = tick * int(filled) + empty * int(
                                            nofill) + '  %7s' %percf
        return graph

    def getMemInfo(self):
        """ Get memory statistics from /proc/meminfo """
        if os.path.isfile(self.target + 'proc/meminfo'):
            mem = Object()
            with open(self.target + 'proc/meminfo', 'r') as meminfo:
                for line in meminfo:
                    if 'MemTotal' in line:
                        mem.total = round(
                                    (int(line.split()[1]) / 1024), 2)
                    elif 'MemFree' in line:
                        mem.free = round(
                                    (int(line.split()[1]) / 1024), 2)
                    elif 'Buffers' in line:
                        mem.buffered = round(
                                    (int(line.split()[1]) / 1024), 2)
                    elif re.match ('^Cached:', line):
                        mem.cached = round(
                                    (int(line.split()[1]) / 1024), 2)
                    elif 'HugePages_Total:' in line:
                        mem.hugepages = int(line.split()[1]) / 1024
                    elif 'HugePages_Free' in line:
                        mem.hugepagesFree = int(line.split()[1]) / 1024
                    elif 'Dirty:' in line:
                        mem.dirty = round(
                                    (int(line.split()[1]) / 1024), 2)
                    elif 'Slab:' in line:
                        mem.slab = round(
                                    (int(line.split()[1]) / 1024), 2)
                    elif 'SwapTotal:' in line:
                        mem.swapTotal = round(
                                    (int(line.split()[1]) / 1024), 2)
                    elif 'SwapFree:' in line:
                        mem.swapFree = round(
                                    int(line.split()[1]) / 1024, 2)

            mem.used = mem.total - mem.free
            mem.inUse = mem.used - mem.cached
            mem.swapUsed = mem.swapTotal - mem.swapFree
            return mem
        else:
            return False

    def getMemSysCtls(self):
        sysctls = Object()
        oom = Object()
        mem = Object()
        ooms = pysosutils.getSysctl(self.target, 'oom')  
        mems = pysosutils.getSysctl(self.target, 'mem')
        for key in ooms:
            setattr(oom, key[key.find('.')+1:len(key)], ooms[key])
        for key in mems:
            setattr(mem, key[key.find('.')+1:len(key)], mems[key])
        mem.swappiness = pysosutils.getSysctl(self.target,
                        'swappiness')['vm.swappiness']
        sysctls.oom = oom
        sysctls.mem = mem
        return sysctls
        
    def getAllMemInfo(self):
        mem = Object()
        mem.mem = self.getMemInfo()
        mem.sysctls = self.getMemSysCtls()
        return mem

    def displayMemGraphs(self):
        """ Use data from getself.memInfo() to display graphed data """

        print colors.BHEADER\
                    + '\t Memory Statistics graphed : ' + colors.ENDC

        print colors.BLUE + '\t\t Used      : %8.2f GB ' %(
                self.mem.used / 1024) + self._graph(round((
                (self.mem.used / self.mem.total) * 100),
                2)) + colors.ENDC

        print colors.CYAN + '\t\t Cached    : %8.2f GB ' %(
                self.mem.cached / 1024) + self._graph(round((
                (self.mem.cached / self.mem.total) * 100),
                2)) + colors.ENDC

        print colors.PURPLE + '\t\t Buffered  : %8.2f GB ' %(
                self.mem.buffered / 1024) + self._graph(round((
                (self.mem.buffered / self.mem.total) * 100),
                2)) + colors.ENDC

        if self.mem.swapTotal > 0:
            print colors.WHITE + '\t\t Swap      : %8.2f MB ' %(
                self.mem.swapUsed) + self._graph(round(((
                self.mem.swapUsed / self.mem.swapTotal) * 100),
                2)) + colors.ENDC

        if self.mem.hugepages > 0:
            print colors.GREEN + '\t\t Hugepages : %8s    ' %(
                self.mem.hugepages) +  self._graph((
                self.mem.hugepagesFree / int(self.mem.hugepages))
                * 100) + colors.ENDC

        print colors.RED + '\t\t Dirty     : %8s MB ' %(
                self.mem.dirty) + self._graph(round(((
                self.mem.dirty / self.mem.total) * 100),
                2)) + colors.ENDC

        print '\t\t SLAB      : %8s MB ' %self.mem.slab + self._graph(
                round(((self.mem.slab / self.mem.total) * 100), 2))

    def displayMemInfo(self):
        """ Display memory statistics from getself.memInfo() """

        print colors.BSECTION + "Memory " + colors.ENDC
        if self.mem == False:
            print colors.BRED +\
                '\t proc/self.memInfo not found - cannot parse'\
                + colors.ENDC
            return False

        self.displayMemGraphs()

        print colors.BHEADER + '\t RAM  :' + colors.ENDC
        print '\t\t %6.2f GB total memory on system' %(math.ceil(
                                        self.mem.total / 1024))
        print colors.BLUE  + '\t\t %6.2f GB (%.2f %%) used' %((
                self.mem.used / 1024), (self.mem.used /
                self.mem.total) * 100) + colors.ENDC

        print colors.CYAN + '\t\t %6.2f GB (%.2f %%) cached' %((
                self.mem.cached / 1024), (self.mem.cached /
                self.mem.total) * 100) + colors.ENDC

        print colors.PURPLE + '\t\t %6.2f GB (%.2f %%) buffered' %((
                self.mem.buffered / 1024), ((self.mem.buffered / 
                self.mem.total) * 100)) + colors.ENDC

        print colors.RED + '\t\t %6.2f MB (%.2f %%) dirty' %(
                self.mem.dirty, (self.mem.dirty / self.mem.total) 
                * 100) + colors.ENDC

        print colors.BHEADER + '\t Swap :' + colors.ENDC
        print colors.WHITE + '\t\t %6.2f GB defined  swap space ' %(
                self.mem.swapTotal / 1024) + colors.ENDC

        if self.mem.swapTotal > 0:
            print colors.WHITE +\
                '\t\t %6.2f MB (%.2f %%) swap space used ' %(
                self.mem.swapUsed, (self.mem.swapUsed /
                self.mem.swapTotal) * 100) + colors.ENDC

        print colors.BHEADER + '\t Misc :'+ colors.ENDC
        print '\t\t %6s MB (%.2f %%) of total memory used for SLAB' %(
                self.mem.slab, (self.mem.slab / self.mem.total))

        if self.mem.hugepages > 0:
            print colors.GREEN + '\t\t %6s total hugepages allocated' %(
                self.mem.hugepages) + colors.ENDC

if __name__ == '__main__':
    target = sys.argv[1]
    test = memory(target=target)
    test.displayMemInfo()
