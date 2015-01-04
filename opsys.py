import sys
import datetime
import textwrap
import re
import pysosutils
import os
from colors import *

class Object(object):
    pass

class opsys:
    """ Capture general information about the OS in the sosreport """

    def __init__(self, target):
        self.target = target

    def getHostName(self):
        """ Get the hostname of the system """
        return pysosutils.fileToString(self.target + 
                                        'sos_commands/general/hostname')

    def getRunLevel(self):
        """ Get the _current_ runlevel """
        return pysosutils.fileToString(self.target + 
                                        'sos_commands/startup/runlevel')

    def getSosDate(self):
        """ Get time of when sosreport was run """
        return pysosutils.fileToString(self.target + 'date')

    def getUptime(self):
        """ Get and format system uptime into a readable string """
        uptime = ''
        u = pysosutils.fileToString(self.target + 
                                        'sos_commands/general/uptime')
        if 'not found' in u:
            return u
        upString = u[u.find('up')+2:u.find('user')-3].strip().strip(',')
        if 'min' in upString:
            return upString
        elif ':' in u:
            days = upString[0:upString.find('day')].strip().strip(',')
            uptime += days + ' days'
            hours = upString[upString.find('day')+4:
                                upString.find(':')].strip().strip(',')
            uptime += hours + ' hours'
            minutes = upString[upString.find(':')+1:
                                len(upString)].strip()
            uptime += ' ' + minutes + ' minutes'
        return uptime

    def getUname(self):
        """ Get contents of uname_-a """
        return pysosutils.fileToString(self.target + 
                                        'sos_commands/kernel/uname_-a')

    def getLoadAvg(self):
        """ Get reported loadavg at time of sosreport """
        uptime = pysosutils.fileToString(self.target + 
                                        'sos_commands/general/uptime')
        index = uptime.find('e:')
        loads = uptime[index+2:len(uptime)].split(',')
        return loads

    def formatLoadAvg(self):
        """ Format getLoadAvg() into string with percentages """
        loads = self.getLoadAvg()
        cpus = self.getCpuInfo().processors
        percs = []
        for item in loads:
            index = loads.index(item)
            loadperc = (float(item) / cpus) * 100
            if loadperc < 75:
                loads[index] = (loads[index] + colors.DBLUE + '(%.2f%%)'
                                    + colors.ENDC) %loadperc
            elif loadperc > 74 and loadperc < 100:
                loads[index] = (loads[index] + colors.WARN + '(%.2f%%)'
                                    + colors.ENDC) %loadperc
            else:
                loads[index] = (loads[index] + colors.BRED
                                + '(%.2f%%)' + colors.ENDC) %loadperc
        return str(loads[0] + loads[1] + loads[2])

    def getProcStat(self):
        """ Get boottime, number of processes and running procs """
        procStat = Object()
        with open(self.target+'proc/stat', 'r') as pfile:
            for line in pfile:
                if line.startswith('btime'):
                    btime = line.split()[1]
                    procStat.boottime = (
                    datetime.datetime.fromtimestamp(
                    int(btime)).strftime('%a %b %d %H:%M:%S UTC %Y'))
                if line.startswith('processes'):
                    procStat.processes = line.split()[1]
                if line.startswith('procs_running'):
                    procStat.procsrun = line.split()[1]
        return procStat

    def getCpuInfo(self, formatFlags=True):
        """ Get data from /proc/cpuinfo """
        cpuInfo = Object()
        with open(self.target+'proc/cpuinfo') as cfile:
            # we read in reverse since the cpu info output is the same
            # no need to iterate over dozens of the same template
            # we can extrapolate the data points that may change once we 
            # assume that the lines being read are for the last CPU
            for line in reversed(cfile.readlines()):
                line = line.rstrip('\n')
                index = line.find(':')
                if line.startswith('flags'):
                    cpuInfo.flags = line[index+2:len(line)]
                # number of physical cores
                elif line.startswith('cpu cores'):
                    cpuInfo.cores = int(line[index+2:len(line)])
                # number of threads per physical core
                elif line.startswith('siblings'):
                    cpuInfo.threadspercore = int(
                                                line[index+2:len(line)])
                # number of physical sockets
                elif line.startswith('physical id'):
                    cpuInfo.sockets = int(line[index+2:len(line)]) +1
                # proc model
                elif line.startswith('model name'):
                    cpuInfo.model = line[index+2:len(line)]
                # proc family
                elif line.startswith('cpu family'):
                    cpuInfo.family = line[index+2:len(line)]
                # proc vendor
                elif line.startswith('vendor_id'):
                    cpuInfo.vendor = line[index+2:len(line)]
                # finally, total number of CPUs
                elif line.startswith('processor'):
                    cpuInfo.processors = int(line[index+2:
                                                        len(line)])+1
                    break

        if formatFlags:
            importantFlags = ['vmx', ' svm ', 'nx', ' lm ']
            for flag in importantFlags:
                pattern = re.compile(flag)
                cpuInfo.flags = pattern.sub(colors.WHITE + flag + 
                                            colors.ENDC, cpuInfo.flags)
        try:
            cpuInfo.sockets
            cpuInfo.undefinedvm = False
        except:
            cpuInfo.undefinedvm = True
            cpuInfo.sockets = 0
            cpuInfo.cores = 0
            cpuInfo.threadspercore = 0
        return cpuInfo

    def getAllOpsys(self):
        op = Object()
        op.cpu = self.getCpuInfo(formatFlags=False)
        op.procs = self.getProcStat()
        op.selinux = pysosutils.getSeLinux(self.target)
        op.loadavg = self.getLoadAvg()
        op.loadavgform = self.formatLoadAvg()
        op.taint = pysosutils.getTaintCodes(self.target)
        op.hostname = self.getHostName()
        op.runlevel = self.getRunLevel()
        op.sosdate = self.getSosDate()
        op.uptime = self.getUptime()
        op.uname = self.getUname()
        op.release = pysosutils.getRelease(self.target)
        return op

    def displayOpSys(self):
        """ Display general OS data """
        procStat = self.getProcStat()
        cpuInfo = self.getCpuInfo()
        selStatus = pysosutils.getSeLinux(self.target)
        loadAvg = self.formatLoadAvg()
        taintCodes = pysosutils.getTaintCodes(self.target)

        print colors.BSECTION + "OS " + colors.ENDC
        print colors.BHEADER + '\t Hostname  : ' + colors.ENDC +\
                                                    self.getHostName()
        print colors.BHEADER +  '\t Release   : ' + colors.ENDC +\
                                    pysosutils.getRelease(self.target)
        print colors.BHEADER + '\t Runlevel  : ' + colors.ENDC +\
                                                    self.getRunLevel()
        print colors.BHEADER +  '\t SELinux   : ' + colors.ENDC +\
                    selStatus['current'] + ' ( config: ' + selStatus[
                                                        'config'] + ' )'

        print colors.BHEADER + '\t Kernel    : ' + colors.ENDC
        print '\t   ' + colors.BBLUE + 'Booted kernel  : '\
                + colors.ENDC + pysosutils.getKernelVersion(self.target)
        print '\t   ' + colors.BBLUE + 'Booted cmdline : '\
                + colors.ENDC
        print '%15s' % ' ' + textwrap.fill(pysosutils.getCmdLine(
                self.target), 90, subsequent_indent='%15s' % ' ')
        print colors.BHEADER + '\t Taints    :' + colors.ENDC +\
                                                        taintCodes[0]

        if len(taintCodes) > 1:
            taintCodes.pop(0)
            for item in taintCodes:
                print '\t\t    ' + item

        print '\t ' + colors.BGREEN + '~ ' * 20 + colors.ENDC
        print colors.BHEADER  + '\t Boot time : ' + colors.ENDC +\
                                                    procStat.boottime
        print colors.BHEADER  + '\t Sys time  : ' + colors.ENDC +\
                                                    self.getSosDate()
        print colors.BHEADER + '\t Uptime    : ' + colors.ENDC +\
                                                    self.getUptime()
        print colors.BHEADER + '\t Load Avg  : ' + colors.WHITE +\
                '[%s CPUs] ' %(
                        cpuInfo.processors) + colors.ENDC + loadAvg

        print colors.BHEADER + '\t /proc/stat: ' + colors.ENDC
        print '\t   ' + colors.BBLUE + 'procs running : '\
        + colors.ENDC + procStat.procsrun  + colors.BLUE +\
        colors.BOLD + '   processes (since boot) : ' + colors.ENDC +\
        procStat.processes

    def displayCpuInfo(self):
        """ Display CPU detail information including flags """
        cpuInfo = self.getCpuInfo()
        print colors.BSECTION + 'CPU' + colors.ENDC
        print colors.WHITE + colors.BOLD + '\t\t ' + str(
            cpuInfo.processors) +' logical processors' + colors.ENDC

        if cpuInfo.sockets > 0:
            print '\t\t ' + str(cpuInfo.sockets) + ' ' +\
                                cpuInfo.model.strip() + ' processors'
            print '\t\t %s cores / %s threads per physical processor' %(
                            cpuInfo.cores, cpuInfo.threadspercore)
        else:
            print colors.BLUE +'\t\t ' +\
            'Virtual Machine with no defined sockets, cores or threads'\
            + colors.ENDC
        print '\t\t flags : ' + textwrap.fill(
                    cpuInfo.flags, 90, subsequent_indent='\t\t\t ')

if __name__ == '__main__':
    target = sys.argv[1]
    test = opsys(target=target)
    test.displayOpSys()
    test.displayCpuInfo()
