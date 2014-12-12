import sys
from collections import defaultdict
from colors import *

class procInfo:
    
    def __init__(self, target):
        self.target = target
        self.psHeader = '\t' + colors.BLUE + colors.BOLD + '{:^6}\t{:^6}\t{:^5} {:^5}  {:^7}  {:^7}  {:^4} {:^4}  {:^5}{:^8}   {:<8}'\
        .format('USER', 'PID', '%CPU', '%MEM', 'VSZ-MB', 'RSS-MB', 'TTY', 'STAT', 'START',\
         'TIME', 'COMMAND') + colors.ENDC
        
    def parseProcFile(self):
        retval = []
        with open(self.target + 'ps', 'r') as psfile:
            psfile.next()
            for line in psfile:
                proc = line.split()
                nfields = len(line.split()) -1
                retval.append(line.split(None, nfields))
        return retval
    
    def getNumProcs(self):
        psInfo = self.parseProcFile()
        return len(psInfo)
        
    def getUserReport(self):
        psInfo = self.parseProcFile()
        usage = defaultdict(list)
        for proc in psInfo:
            value = psInfo[psInfo.index(proc)]
            # here we are checking the process' owner 
            # if the owner has been seen we add up the process' CPU and memory values
            if usage.has_key(value[0]):
    
                usage[value[0]][0] += float(value[2])
                usage[value[0]][1] += float(value[3])
                usage[value[0]][2] += float(value[5])
            else:
            # if it hasn't been seen we add a new key to the dictionary with the name of the user
            # this allows the above to catch repeats (root for example) and tally total
            # CPU and memory values on a per user basis    
                usage[value[0]] = [float(value[2]), float(value[3]), float(value[5])]

        userReport = sorted(usage.items(), reverse=True, key=lambda x: x[1][2])
        
        return userReport
        
    def _formatTopReport(self, psInfo, reportNum=5):
        report = []
        for i in xrange(0, int(reportNum)):
            ps = psInfo[i]
            ps[4] = int(ps[4]) / 1024
            ps[5] = int(ps[5]) / 1024
            cmd = ''
            for i in xrange(10, 13):
                try:
                    cmd = cmd + ' ' + str(ps[i]).strip('\n')
            
                except:
                    pass
            report.append([ps[0], ps[1], ps[2], ps[3], ps[4], ps[5], ps[6], ps[7], ps[8], ps[9], cmd[0:65]])
        return report
            
    def getTopMem(self, reportNum=5):
        psInfo = self.parseProcFile()
        psInfo.sort(reverse=True, key=lambda x: float(x[5]))
        topMemReport = self._formatTopReport(psInfo)
        return topMemReport
        
    def getTopCpu(self, reportNum=5):
        psInfo = self.parseProcFile()
        psInfo.sort(reverse=True, key=lambda x: float(x[2]))
        topCpuReport = self._formatTopReport(psInfo)
        return topCpuReport
        
    def getDefunctProcs(self):
        psInfo = self.parseProcFile()
        badProcs = []
        for item in psInfo:
            value = psInfo[psInfo.index(item)]
            if any('<defunct>' in item for item in value) or any('D' in item for item in value[7]) or any('Ds' in item for item in value[7]):
                badProcs.append(value)
        return badProcs
    
    def _displayReport(self, report):

        print self.psHeader
        for ps in report:
            print '\t{:^8} {:^6}\t{:^5} {:^5}  {:<7.0f}  {:<7.0f}  {:^5} {:^4} {:^6} {:<9}{}'.format(ps[0], ps[1], ps[2], ps[3], ps[4], ps[5], ps[6], ps[7], ps[8], ps[9], ps[10])
    
    def displayTopReport(self):
        numProcs = self.getNumProcs()
        usageReport = self.getUserReport()
        
        print colors.HEADER_BOLD + 'PS' + colors.ENDC
        print '\t' + colors.WHITE + 'Total processes : ' + colors.ENDC + str(numProcs) +'\n'
        
        print '\t' + colors.WHITE + 'Top Users of CPU and MEM : ' + colors.ENDC
        print '\t ' + colors.BLUE + colors.BOLD + '{:10}  {:6}  {:6}  {:8}'.format('USER', '%CPU', '%MEM', 'RSS') + colors.ENDC

        for i in xrange(0, 4):
            value = usageReport[i]
            print '\t {:<10}  {:^6.2f}  {:^6.2f}  {:>3.2f} GB'.format(value[0], value[1][0], value[1][1], int(value[1][2]) / 1048576)
        print ''

    def displayCpuReport(self):
        cpuReport = self.getTopCpu()
        print '\t' + colors.WHITE + 'Top CPU processes : ' + colors.ENDC
        self._displayReport(cpuReport)
        print ''
        
    def displayMemReport(self):
        memReport = self.getTopMem()
        print '\t' + colors.WHITE + 'Top Memory processes : ' + colors.ENDC
        self._displayReport(memReport)
        print ''
    
    def displayDefunctReport(self):
        defunctReport = self.getDefunctProcs()
        if defunctReport:
            print '\t' + colors.WHITE + 'Uninterruptable Sleep and Defunct Processes : ' + colors.ENDC
            defunctReport = self._formatTopReport(defunctReport, reportNum=len(defunctReport))
            self._displayReport(defunctReport)
            print ''                
    
    def displayPsInfo(self):
        self.displayTopReport()
        self.displayDefunctReport()
        self.displayCpuReport()
        self.displayMemReport()


if __name__ == '__main__':
    target = sys.argv[1]
    test = procInfo(target)
    test.displayPsInfo()
        
