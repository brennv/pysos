import sys, os, re
from colors import *

class memory:
    
    def __init__(self, target):
        self.target = target
        
    def graph(self, perc):

        # general graphing function, needs to be fed a percentage. 
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
    
    def memInfo(self):
        if os.path.isfile(self.target + 'proc/meminfo'):
            memInfo = {}
            with open(self.target + 'proc/meminfo', 'r') as meminfo:
                for line in meminfo:
                    if 'MemTotal' in line:
                        memInfo['total'] = round((int(line.split()[1]) / 1024), 2)
                    elif 'MemFree' in line:
                        memInfo['free'] = round((int(line.split()[1]) / 1024), 2)
                    elif 'Buffers' in line:
                        memInfo['buffered'] = round((int(line.split()[1]) / 1024), 2)
                    elif re.match ('^Cached:', line):
                        memInfo['cached'] = round((int(line.split()[1]) / 1024), 2)
                    elif 'HugePages_Total:' in line:
                        memInfo['hugepages'] = int(line.split()[1]) / 1024
                    elif 'HugePages_Free' in line:
                        memInfo['hugepagesFree'] = int(line.split()[1]) / 1024
                    elif 'Dirty:' in line:
                        memInfo['dirty'] = round((int(line.split()[1]) / 1024), 2)
                    elif 'Slab:' in line:
                        memInfo['slab'] = round((int(line.split()[1]) / 1024), 2)
                    elif 'SwapTotal:' in line:
                        memInfo['swapTotal'] = round((int(line.split()[1]) / 1024), 2)
                    elif 'SwapFree:' in line:
                        memInfo['swapFree'] = round(int(line.split()[1]) / 1024, 2)
            

            memInfo['used'] = memInfo['total'] - memInfo['free']
            memInfo['inUse'] = memInfo['used'] = memInfo['cached']
            memInfo['swapUsed'] = memInfo['swapTotal'] - memInfo['swapFree']

            return memInfo
        else:
            return False
            
    def displayMemGraphs(self):
        memInfo = self.memInfo()
        print colors.SECTION + colors.BOLD + "Memory " + colors.ENDC
        print colors.HEADER + colors.BOLD + '\t Memory Statistics graphed : ' + colors.ENDC
        
        print colors.BLUE + '\t\t Used      : %8.2f GB ' %(memInfo['used'] / 1024)\
            + self.graph(round(((memInfo['used'] / memInfo['total']) * 100), 2)) + colors.ENDC
        
        print colors.CYAN + '\t\t Cached    : %8.2f GB ' %(memInfo['cached'] / 1024)\
        + self.graph(round(((memInfo['cached'] / memInfo['total']) * 100), 2)) + colors.ENDC
        
        print colors.PURPLE + '\t\t Buffered  : %8.2f GB ' %(memInfo['buffered'] / 1024)\
            + self.graph(round(((memInfo['buffered'] / memInfo['total']) * 100), 2)) + colors.ENDC
        
        print colors.WHITE + '\t\t Swap      : %8.2f MB ' % memInfo['swapUsed']\
            + self.graph(round(((memInfo['swapUsed'] / memInfo['swapTotal']) * 100), 2)) + colors.ENDC
        
        if memInfo['hugepages'] > 0:
            print colors.GREEN + '\t\t Hugepages : %8s    ' %memInfo['hugepages']\
                +  self.graph((memInfo['hugepagesFree'] / int(memInfo['hugepages'])) * 100) + colors.ENDC
        
        print colors.RED + '\t\t Dirty     : %8s MB ' %memInfo['dirty']\
            +  self.graph(round(((memInfo['dirty'] / memInfo['total']) * 100), 2)) + colors.ENDC
        
        print '\t\t SLAB      : %8s MB ' %memInfo['slab']\
            +  self.graph(round(((memInfo['slab'] / memInfo['swapTotal']) * 100), 2))
    
    def displayMemInfo(self):
        memInfo = self.memInfo()
        self.displayMemGraphs()
        print colors.HEADER + colors.BOLD + '\t RAM  :' + colors.ENDC
        print '\t\t %6.2f GB total memory on system' %(round(memInfo['total'] / 1024) +1)
        print colors.BLUE  + '\t\t %6.2f GB (%.2f %%) used' %((memInfo['used'] / 1024), (memInfo['used'] / memInfo['total']) * 100) + colors.ENDC
        print colors.CYAN + '\t\t %6.2f GB (%.2f %%) cached' %((memInfo['cached'] / 1024), (memInfo['cached'] / memInfo['total']) * 100) + colors.ENDC
        print colors.PURPLE + '\t\t %6.2f GB (%.2f %%) buffered' %((memInfo['buffered'] / 1024), ((memInfo['buffered'] / memInfo['total']) * 100)) + colors.ENDC
        print colors.RED + '\t\t %6.2f MB (%.2f %%) dirty' %(memInfo['dirty'], (memInfo['dirty'] / memInfo['total']) * 100) + colors.ENDC
          
        print colors.HEADER + colors.BOLD + '\t Swap :' + colors.ENDC
        print colors.WHITE + '\t\t %6.2f GB defined  swap space ' %(memInfo['swapTotal'] / 1024) + colors.ENDC
        print colors.WHITE + '\t\t %6.2f MB (%.2f %%) swap space used ' %(memInfo['swapUsed'], (memInfo['swapUsed'] / memInfo['swapTotal']) * 100) + colors.ENDC

        print colors.HEADER + colors.BOLD + '\t Misc :'+ colors.ENDC
        print '\t\t %6s MB (%.2f %%) of total memory used for SLAB' %(memInfo['slab'], (memInfo['slab'] / memInfo['total']))
        if memInfo['hugepages'] > 0:
            print colors.GREEN + '\t\t %6s total hugepages allocated' %(memInfo['hugepages']) + colors.ENDC
        
        
if __name__ == '__main__':
    target = sys.argv[1]
    test = memory(target=target)
    test.displayMemInfo(memInfo)
    
