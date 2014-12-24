import sys
import os
import re
import math
from colors import *

class memory:
    """ Capture and optionally display memory related data """

    def __init__(self, target):
        self.target = target
        self.memInfo = self.getMemInfo()

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
        graph = tick * int(filled) + empty * int(nofill) + '  %7s' %percf
        return graph

    def getMemInfo(self):
        """ Get memory statistics from /proc/meminfo """
        if os.path.isfile(self.target + 'proc/meminfo'):
            memInfo = {}
            with open(self.target + 'proc/meminfo', 'r') as meminfo:
                for line in meminfo:
                    if 'MemTotal' in line:
                        memInfo['total'] = round(
                                    (int(line.split()[1]) / 1024), 2)
                    elif 'MemFree' in line:
                        memInfo['free'] = round(
                                    (int(line.split()[1]) / 1024), 2)
                    elif 'Buffers' in line:
                        memInfo['buffered'] = round(
                                    (int(line.split()[1]) / 1024), 2)
                    elif re.match ('^Cached:', line):
                        memInfo['cached'] = round(
                                    (int(line.split()[1]) / 1024), 2)
                    elif 'HugePages_Total:' in line:
                        memInfo['hugepages'] = int(
                                                line.split()[1]) / 1024
                    elif 'HugePages_Free' in line:
                        memInfo['hugepagesFree'] = int(
                                                line.split()[1]) / 1024
                    elif 'Dirty:' in line:
                        memInfo['dirty'] = round(
                                    (int(line.split()[1]) / 1024), 2)
                    elif 'Slab:' in line:
                        memInfo['slab'] = round(
                                    (int(line.split()[1]) / 1024), 2)
                    elif 'SwapTotal:' in line:
                        memInfo['swapTotal'] = round(
                                    (int(line.split()[1]) / 1024), 2)
                    elif 'SwapFree:' in line:
                        memInfo['swapFree'] = round(
                                    int(line.split()[1]) / 1024, 2)

            memInfo['used'] = memInfo['total'] - memInfo['free']
            memInfo['inUse'] = memInfo['used'] = memInfo['cached']
            memInfo['swapUsed'] = memInfo['swapTotal'] - memInfo['swapFree']
            return memInfo
        else:
            return False

    def displayMemGraphs(self):
        """ Use the data from getself.memInfo() to display graphed data """

        print colors.HEADER + colors.BOLD\
                    + '\t Memory Statistics graphed : ' + colors.ENDC

        print colors.BLUE + '\t\t Used      : %8.2f GB ' %(
                self.memInfo['used'] / 1024) + self._graph(round((
                (self.memInfo['used'] / self.memInfo['total']) * 100),
                2)) + colors.ENDC

        print colors.CYAN + '\t\t Cached    : %8.2f GB ' %(
                self.memInfo['cached'] / 1024) + self._graph(round((
                (self.memInfo['cached'] / self.memInfo['total']) * 100),
                2)) + colors.ENDC

        print colors.PURPLE + '\t\t Buffered  : %8.2f GB ' %(
                self.memInfo['buffered'] / 1024) + self._graph(round((
                (self.memInfo['buffered'] / self.memInfo['total']) * 100),
                2)) + colors.ENDC

        if self.memInfo['swapTotal'] > 0:
            print colors.WHITE + '\t\t Swap      : %8.2f MB ' %(
                self.memInfo['swapUsed']) + self._graph(round(((
                self.memInfo['swapUsed'] / self.memInfo['swapTotal']) * 100),
                2)) + colors.ENDC

        if self.memInfo['hugepages'] > 0:
            print colors.GREEN + '\t\t Hugepages : %8s    ' %(
                self.memInfo['hugepages']) +  self._graph((
                self.memInfo['hugepagesFree'] / int(self.memInfo['hugepages']))
                * 100) + colors.ENDC

        print colors.RED + '\t\t Dirty     : %8s MB ' %(
                self.memInfo['dirty']) + self._graph(round(((
                self.memInfo['dirty'] / self.memInfo['total']) * 100),
                2)) + colors.ENDC

        print '\t\t SLAB      : %8s MB ' %self.memInfo['slab'] + self._graph(
                round(((self.memInfo['slab'] / self.memInfo['total']) * 100), 2))

    def displayMemInfo(self):
        """ Display memory statistics from getself.memInfo() """

        print colors.SECTION + colors.BOLD + "Memory " + colors.ENDC
        if self.memInfo == False:
            print colors.RED + colors.BOLD +\
                '\t proc/self.memInfo not found - cannot parse' + colors.ENDC
            return False

        self.displayMemGraphs()

        print colors.HEADER + colors.BOLD + '\t RAM  :' + colors.ENDC
        print '\t\t %6.2f GB total memory on system' %(math.ceil(
                                        self.memInfo['total'] / 1024))
        print colors.BLUE  + '\t\t %6.2f GB (%.2f %%) used' %((
                self.memInfo['used'] / 1024), (self.memInfo['used'] /
                self.memInfo['total']) * 100) + colors.ENDC

        print colors.CYAN + '\t\t %6.2f GB (%.2f %%) cached' %((
                self.memInfo['cached'] / 1024), (self.memInfo['cached']/
                self.memInfo['total']) * 100) + colors.ENDC

        print colors.PURPLE + '\t\t %6.2f GB (%.2f %%) buffered' %((
                self.memInfo['buffered'] / 1024), (
                (self.memInfo['buffered'] / self.memInfo['total']) *
                100)) + colors.ENDC

        print colors.RED + '\t\t %6.2f MB (%.2f %%) dirty' %(
                self.memInfo['dirty'], (self.memInfo['dirty'] /
                self.memInfo['total']) * 100) + colors.ENDC

        print colors.HEADER + colors.BOLD + '\t Swap :' + colors.ENDC
        print colors.WHITE + '\t\t %6.2f GB defined  swap space ' %(
                self.memInfo['swapTotal'] / 1024) + colors.ENDC

        if self.memInfo['swapTotal'] > 0:
            print colors.WHITE +\
                '\t\t %6.2f MB (%.2f %%) swap space used ' %(
                self.memInfo['swapUsed'], (self.memInfo['swapUsed'] /
                self.memInfo['swapTotal']) * 100) + colors.ENDC

        print colors.HEADER + colors.BOLD + '\t Misc :'+ colors.ENDC
        print '\t\t %6s MB (%.2f %%) of total memory used for SLAB' %(
                self.memInfo['slab'], (self.memInfo['slab'] /
                                                self.memInfo['total']))

        if self.memInfo['hugepages'] > 0:
            print colors.GREEN + '\t\t %6s total hugepages allocated' %(
                self.memInfo['hugepages']) + colors.ENDC

if __name__ == '__main__':
    target = sys.argv[1]
    test = memory(target=target)
    test.displayMemInfo(memInfo)
