import sys
import os
import re
import math
from . import pysosutils
from .colors import Color as c


class Object(object):
    pass


class memory:

    """ Capture and optionally display memory related data """

    def __init__(self, target):
        self.target = target
        self.mem = self.getMemInfo()
        self.pprint = c()

    def _graph(self, perc):
        """
        General graphing function to spit out a line graph.

        Needs to be fed a percentage as th 'perc' arg.
        """
        tick = "◆"
        empty = "◇"
        if perc == 0:
            filled = 0
        else:
            filled = round(40 * (perc / 100))
        nofill = 40 - filled
        percf = '%.2f' % perc + ' %'
        graph = tick * int(filled) + empty * int(
            nofill) + '  %7s' % percf
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
                    elif re.match('^Cached:', line):
                        mem.cached = round(
                            (int(line.split()[1]) / 1024), 2)
                    elif 'HugePages_Total:' in line:
                        mem.hugepages = int(line.split()[1])
                    elif 'HugePages_Free' in line:
                        mem.hugepagesfree = int(line.split()[1])
                        mem.hugepagesused = (mem.hugepages -
                                             mem.hugepagesfree)
                    elif 'HugePages_Rsvd' in line:
                        mem.hugepagesrsvd = int(line.split()[1])
                    elif 'Hugepagesize' in line:
                        mem.hugepagesize = int(line.split()[1])
                        mem.hugepagesallocation = (mem.hugepagesize *
                                                   mem.hugepages)
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

            try:
                mem.hugepagesperc = round(((float(mem.hugepagesused) /
                                            float(mem.hugepages)) * 100), 2)
            except:
                pass
            mem.used = mem.total - mem.free
            mem.inuse = mem.used - mem.cached
            mem.swapUsed = mem.swapTotal - mem.swapFree
            mem.usedperc = round(((mem.used / mem.total) * 100), 2)
            mem.cachedperc = round(((mem.cached / mem.total) * 100), 2)
            mem.freeperc = round(((mem.free / mem.total) * 100), 2)
            mem.bufferedperc = round(((mem.buffered / mem.total) * 100), 2)
            mem.inuseperc = round(((mem.inuse / mem.total) * 100), 2)
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
            setattr(oom, key[key.find('.') + 1:len(key)], ooms[key])
        for key in mems:
            setattr(mem, key[key.find('.') + 1:len(key)], mems[key])
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

        self.pprint.bheader('\t Memory Statistics graphed')
        self.pprint.blue('\t\t Used      : %8.2f GB ' % (
            self.mem.inuse / 1024) + self._graph(
            self.mem.inuseperc
        )
        )

        self.pprint.cyan('\t\t Cached    : %8.2f GB ' % (
            self.mem.cached / 1024) + self._graph(
            self.mem.cachedperc
        )
        )

        self.pprint.purple('\t\t Buffered  : %8.2f GB ' % (
            self.mem.buffered / 1024) + self._graph(
            self.mem.bufferedperc
        )
        )

        if self.mem.swapTotal > 0:
            self.pprint.white('\t\t Swap      : %8.2f MB ' % (
                self.mem.swapUsed) + self._graph(round(((
                    self.mem.swapUsed / self.mem.swapTotal) * 100),
                    2)
            )
            )

        if self.mem.hugepages > 0:
            self.pprint.green('\t\t Hugepages : %8s    ' % (
                self.mem.hugepagesused) + self._graph(
                self.mem.hugepagesperc
            )
            )

        self.pprint.red('\t\t Dirty     : %8s MB ' % (
                        self.mem.dirty) + self._graph(round(((
                            self.mem.dirty / self.mem.total) * 100), 2)
        )
        )

        self.pprint.grey('\t\t SLAB      : %8.2f MB ' % (
            self.mem.slab) + self._graph(round(((
                self.mem.slab / self.mem.total) * 100), 2)
        )
        )

    def displayMemInfo(self):
        """ Display memory statistics from getself.memInfo() """

        self.pprint.bsection('Memory')
        if not self.mem:
            self.pprint.bred(
                '\t proc/self.memInfo not found - cannot parse'
            )
            return False

        self.displayMemGraphs()

        print('')
        self.pprint.bheader('\t RAM  :')
        print('\t\t %6.2f GB total memory on system' % (math.ceil(
            self.mem.total / 1024)))
        self.pprint.blue('\t\t %6.2f GB (%.2f %%) used' % ((
            self.mem.inuse / 1024), (self.mem.used /
                                     self.mem.total) * 100)
        )

        self.pprint.cyan('\t\t %6.2f GB (%.2f %%) cached' % ((
            self.mem.cached / 1024), (self.mem.cached /
                                      self.mem.total) * 100)
        )

        self.pprint.purple('\t\t %6.2f GB (%.2f %%) buffered' % ((
            self.mem.buffered / 1024), ((self.mem.buffered /
                                         self.mem.total) * 100))
        )

        self.pprint.red('\t\t %6.2f MB (%.2f %%) dirty' % (
            self.mem.dirty, (self.mem.dirty / self.mem.total) * 100
            )
        )

        self.pprint.bheader('\t Swap :')
        self.pprint.grey('\t\t %6.2f GB defined  swap space ' % (
            self.mem.swapTotal / 1024)
        )

        if self.mem.swapTotal > 0:
            self.pprint.white(
                '\t\t %6.2f MB (%.2f %%) swap space used ' % (
                    self.mem.swapUsed, (self.mem.swapUsed /
                                        self.mem.swapTotal) * 100)
            )

        if self.mem.hugepages > 0:
            self.pprint.bheader('\t HugePages :')
            self.pprint.green('\t\t %6s total hugepages allocated' % (
                self.mem.hugepages)
            )
            self.pprint.green('\t\t %6s (%2.2f %%) hugepages in use'
                              % (self.mem.hugepagesused, self.mem.hugepagesperc
                                 )
                              )

        self.pprint.bheader('\t Misc :')
        self.pprint.grey(
            '\t\t %6s MB (%.2f %%) of total memory used for SLAB' % (
                self.mem.slab, (self.mem.slab / self.mem.total))
        )

if __name__ == '__main__':
    target = sys.argv[1]
    test = memory(target=target)
    test.displayMemInfo()
