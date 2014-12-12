import sys, datetime, textwrap, re, pysosutils, os
from colors import *

class opsys:
    
    def __init__(self, target):
        self.target = target

    def getHostName(self):
        return pysosutils.fileToString(self.target+'sos_commands/general/hostname')

    def getRunLevel(self):
        return pysosutils.fileToString(self.target+'sos_commands/startup/runlevel')

    def getSosDate(self):
        return pysosutils.fileToString(self.target+'date')

    def getUptime(self):
        uptime = ''
        u = pysosutils.fileToString(self.target+'sos_commands/general/uptime')
        if 'not found' in u:
            return u
        idx1 = u.find('up')
        idx2 = u.find('users')
        u = u[idx1+2:idx2-4].replace(',',' ')
        days = u[0:u.find('day')].strip()
        uptime += days + ' days'
        if ':' in u:
            hours = u[u.find('day')+4:u.find(':')].strip()
            uptime += ' ' + hours + ' hours'
            minutes = u[u.find(':')+1:len(u)].strip()
            uptime += ' ' + minutes + ' minutes'
        return uptime

    def getUname(self):
        return pysosutils.fileToString(self.target+'sos_commands/kernel/uname_-a')

    def getLoadAvg(self):
        uptime = pysosutils.fileToString(self.target+'sos_commands/general/uptime')
        index = uptime.find('e:')
        loads = uptime[index+2:len(uptime)].split(',')
        return loads

    def formatLoadAvg(self):
        loads = self.getLoadAvg()
        cpus = self.getCpuInfo()['processors']
        percs = []
        for item in loads:
            index = loads.index(item)
            loadperc = (float(item) / cpus) * 100
            if loadperc < 75:
                loads[index] = (loads[index] + colors.DBLUE + '(%.2f%%)' + colors.ENDC) %loadperc
            elif loadperc > 74 and loadperc < 100:
                loads[index] = (loads[index] + colors.WARN + '(%.2f%%)' + colors.ENDC) %loadperc
            else:
                loads[index] = (loads[index] + colors.RED + colors.BOLD + '(%.2f%%)' + colors.ENDC) %loadperc
        return str(loads[0] + loads[1] + loads[2])
        
    def getProcStat(self):
        procStat = {}
        with open(self.target+'proc/stat', 'r') as pfile:
            for line in pfile:
                if line.startswith('btime'):
                    btime = line.split()[1]
                    procStat['boottime'] = datetime.datetime.fromtimestamp(int(btime)).strftime('%a %b %d %H:%M:%S UTC %Y')
                if line.startswith('processes'):
                    procStat['processes'] = line.split()[1]
                if line.startswith('procs_running'):
                    procStat['procs_running'] = line.split()[1]
        return procStat

    def getCpuInfo(self):
        cpuInfo = {}
        with open(self.target+'proc/cpuinfo') as cfile:
            # we read in reverse since the cpu info output is all the same
            # no need to iterate over potentially dozens of the same template
            # we can extrapolate the data points that may change easily once we 
            # assume that the lines being read are for the last of the CPUs
            for line in reversed(cfile.readlines()):
                line = line.rstrip('\n')
                index = line.find(':')
                if line.startswith('flags'):
                    cpuInfo['flags'] = line[index+2:len(line)]
                # number of physical cores
                elif line.startswith('cpu cores'):
                    cpuInfo['cores'] = line[index+2:len(line)]
                # number of threads per physical core
                elif line.startswith('siblings'):
                    cpuInfo['threadsPerCore'] = line[index+2:len(line)]
                # number of physical sockets
                elif line.startswith('physical id'):
                    cpuInfo['sockets'] = int(line[index+2:len(line)]) +1
                # proc model
                elif line.startswith('model name'):
                    cpuInfo['model'] = line[index+2:len(line)]
                # proc family
                elif line.startswith('cpu family'):
                    cpuInfo['family'] = line[index+2:len(line)]
                # proc vendor
                elif line.startswith('vendor_id'):
                    cpuInfo['vendor'] = line[index+2:len(line)]
                # finally, total number of CPUs
                elif line.startswith('processor'):
                    cpuInfo['processors'] = int(line[index+2:len(line)])+1
                    break

        importantFlags = ['vmx', ' svm ', 'nx', ' lm ']
        for flag in importantFlags:
            pattern = re.compile(flag)
            cpuInfo['flags'] = pattern.sub(colors.WHITE + flag + colors.ENDC, cpuInfo['flags'])
        return cpuInfo

    def displayOpSys(self):
        procStat = self.getProcStat()
        cpuInfo = self.getCpuInfo()
        selStatus = pysosutils.getSeLinux(self.target)
        loadAvg = self.formatLoadAvg()
        taintCodes = pysosutils.getTaintCodes(self.target)

        print colors.SECTION + colors.BOLD + "OS " + colors.ENDC
        print colors.HEADER_BOLD + '\t Hostname  : ' + colors.ENDC + self.getHostName()
        print colors.HEADER_BOLD +  '\t Release   : ' + colors.ENDC + pysosutils.getRelease(self.target)
        print colors.HEADER_BOLD + '\t Runlevel  : ' + colors.ENDC + self.getRunLevel()
        print colors.HEADER_BOLD +  '\t SELinux   : ' + colors.ENDC + selStatus['current'] + ' ( config: ' + selStatus['config'] + ' )'

        print colors.HEADER_BOLD + '\t Kernel    : ' + colors.ENDC
        print '\t   ' + colors.BLUE + colors.BOLD + 'Booted kernel  : ' + colors.ENDC + pysosutils.getKernelVersion(self.target)
        print '\t   ' + colors.BLUE + colors.BOLD + 'Booted cmdline : ' + colors.ENDC
        print '%15s' % ' ' + textwrap.fill(pysosutils.getCmdLine(self.target), 90, subsequent_indent='%15s' % ' ')
        print colors.HEADER_BOLD + '\t Taints    :' + colors.ENDC + taintCodes[0]
        if len(taintCodes) > 1:
            taintCodes.pop(0)
            for item in taintCodes:
                print '\t\t    ' + item
        print colors.GREEN + '%9s' % ' ' + colors.BOLD + '~ ' * 20 + colors.ENDC
        print colors.HEADER_BOLD  + '\t Boot time : ' + colors.ENDC + procStat['boottime']
        print colors.HEADER_BOLD  + '\t Sys time  : ' + colors.ENDC + self.getSosDate()
        print colors.HEADER_BOLD + '\t Uptime    : ' + colors.ENDC + self.getUptime()
        print colors.HEADER_BOLD + '\t Load Avg  : ' + colors.WHITE +'[%s CPUs] ' %cpuInfo['processors'] + colors.ENDC \
            + loadAvg
        print colors.HEADER_BOLD + '\t /proc/stat: ' + colors.ENDC
        print '\t   ' + colors.BLUE + colors.BOLD + 'procs_running : ' + colors.ENDC + procStat['procs_running']  + colors.BLUE + colors.BOLD + '   processes (since boot) : ' + colors.ENDC + procStat['processes']

    def displayCpuInfo(self):
        cpuInfo = self.getCpuInfo()
        print colors.SECTION + colors.BOLD + 'CPU' + colors.ENDC
        print colors.WHITE + colors.BOLD + '\t\t ' + str(cpuInfo['processors']) +' logical processors' + colors.ENDC
        print '\t\t ' + str(cpuInfo['sockets']) + ' ' + cpuInfo['model'].strip() + ' processors'
        print '\t\t %s cores / %s threads per physical processor' %(cpuInfo['cores'], cpuInfo['threadsPerCore'])
        print '\t\t flags : ' + textwrap.fill(cpuInfo['flags'], 90, subsequent_indent='\t\t\t ')


if __name__ == '__main__':
    target = sys.argv[1]
    test = opsys(target=target)
    test.displayOpSys()
    test.displayCpuInfo()
