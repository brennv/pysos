import sys
import os
from colors import *

class Object(object):
    pass

class procInfo:
    """ Get and optionally display information from ps output """

    def __init__(self, target):
        self.target = target
        self.psInfo = self.parseProcFile()

    def parseProcFile(self):
        """ 
        Parse through a ps output file and return the contents
        as list vaues
        """
        if os.path.isfile(
                self.target + 'sos_commands/process/ps_auxwww'):
            psInfo = []
            stats = ['user', 'pid', 'cpu', 'mem', 'vsz', 'rss',
                            'tty', 'stat', 'start', 'time']
            with open(self.target +
                    'sos_commands/process/ps_auxwww', 'r') as psfile:
                psfile.next()
                for line in psfile:
                    proc = Object()
                    line = line.split()
                    for x, stat in enumerate(stats):
                        setattr(proc, stat, line[x])
                    proc.command = ' '.join(line[10:-1])
                    psInfo.append(proc)
            return psInfo
        else:
            return False

    def getNumProcs(self):
        """ Get the number of processes running """
        return len(self.psInfo)

    def getUserReport(self):
        """ Get a report on CPU and RSS usage by user """
        usage = []
        for proc in self.psInfo:
            newProc = True
            if len(usage) > 0 :
                for p in usage:
                    if p.user == proc.user:
                        p.cpu += float(proc.cpu)
                        p.mem += float(proc.mem)
                        p.rss += int(proc.rss)
                        newProc = False
                        break
            if newProc:
                proc.cpu = float(proc.cpu)
                proc.mem = float(proc.mem)
                proc.rss = int(proc.rss)
                usage.append(proc)
        userReport = sorted(usage, reverse=True, 
                            key=lambda x: x.cpu)
        return userReport

    def _formatTopReport(self, psInfo, reportNum=5):
        report = []
        for i in xrange(0, int(reportNum)):
            proc = self.psInfo[i]
            proc.vsz = int(proc.vsz) / 1024
            proc.rss = int(proc.rss) / 1024
            cmd = ''
            for i in xrange(10, 13):
                try:
                    cmd = str(proc.command).strip('\n')
            
                except:
                    pass
            report.append(proc)
        return report

    def getTopMem(self, reportNum=5):
        """ Get report on top memory consuming processes """
        topMemReport = self._formatTopReport(self.psInfo.sort(
                            reverse=True, key=lambda x: float(x.rss)))
        return topMemReport

    def getTopCpu(self, reportNum=5):
        """ Get report on top CPU consuming processes """
        topCpuReport = self._formatTopReport(self.psInfo.sort(
                            reverse=True, key=lambda x: float(x.cpu)))
        return topCpuReport

    def getDefunctProcs(self):
        """ Get report of all defunct processess """
        badProcs = []
        for proc in self.psInfo:
            if ('<defunct>' in proc.command or
                    'D' in proc.stat or
                    'Ds' in proc.stat):
                badProcs.append(value)
        return badProcs

    def displayReport(self, report):

        print '\t' + colors.BBLUE +\
        '{:^6}\t{:^6}\t{:^5} {:^5}  {:^7}  {:^7}  {:^4} {:^4}  {:^5}{:^8}  {:<8}'\
        .format('USER', 'PID', '%CPU', '%MEM', 'VSZ-MB', 'RSS-MB',
            'TTY', 'STAT', 'START', 'TIME', 'COMMAND') + colors.ENDC

        for proc in report:
            print '\t{:^8} {:^6}\t{:^5} {:^5}  {:<7.0f}  {:<7.0f}  {:^5} {:^4} {:^6} {:<9}{}'.format(
                    proc.user, proc.pid,
                    proc.cpu, proc.mem, proc.vsz, proc.rss, proc.tty,
                    proc.stat, proc.start, proc.time,
                    proc.command[0:45].strip())

    def displayTopReport(self):
        """ Display report from getUserReport() """
        numProcs = self.getNumProcs()
        usageReport = self.getUserReport()
        print '\t' + colors.WHITE + 'Total Processes : ' + colors.ENDC \
                + str(numProcs) +'\n'

        print '\t' + colors.WHITE + 'Top Users of CPU and Memory : ' + \
                colors.ENDC
        print '\t ' + colors.BBLUE + \
            '{:10}  {:6}  {:6}  {:8}'.format('USER', '%CPU', '%MEM', 
                                                'RSS') + colors.ENDC

        for i in xrange(0, 4):
            proc = usageReport[i]
            print '\t {:<10}  {:^6.2f}  {:^6.2f}  {:>3.2f} GB'.format(
                    proc.user, proc.cpu, proc.mem,
                    int(proc.rss) / 1048576)
        print ''

    def displayCpuReport(self):
        """ Display report from getTopCpu() """
        cpuReport = self.getTopCpu()
        print '\t' + colors.WHITE + 'Top CPU Consuming Processes : '\
                + colors.ENDC
        self.displayReport(cpuReport)
        print ''

    def displayMemReport(self):
        """ Display report from getTopMem() """
        memReport = self.getTopMem()
        print '\t' + colors.WHITE + 'Top Memory Consuming Processes : '\
                + colors.ENDC
        self.displayReport(memReport)
        print ''

    def displayDefunctReport(self):
        """ Display report from getDefunctProcs() """
        defunctReport = self.getDefunctProcs()
        if defunctReport:
            print '\t' + colors.RED + \
                    'Uninterruptable Sleep and Defunct Processes : ' \
                    + colors.ENDC
            defunctReport = self._formatTopReport(defunctReport, 
                                        reportNum=len(defunctReport))
            self.displayReport(defunctReport)
            print ''

    def displayPsInfo(self):
        """ display ps information for top consumers, CPU, memory and
        defunct process, if any """
        print colors.BSECTION + 'PS' + colors.ENDC
        if self.psInfo:
            self.displayTopReport()
            self.displayDefunctReport()
            self.displayCpuReport()
            self.displayMemReport()
        else:
            print colors.RED + colors.WARN + 'No PS information found' \
                + colors.ENDC

if __name__ == '__main__':
    target = sys.argv[1]
    test = procInfo(target)
    test.displayPsInfo()
