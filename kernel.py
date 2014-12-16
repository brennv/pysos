import sys, os, pysosutils, opsys, filesys, memory, math
from colors import *

class kernel:
    
    def __init__(self, target):
        
        self.target = target
        
    def getKdumpState(self):
        return pysosutils.getChkConfig(self.target, 'kdump')
    
    def getKdumpVersion(self):
        return pysosutils.getRpm(self.target, 'kexec-tools')
        
    def getKdumpConfig(self):
        kdumpConfig = {}
        if os.path.isfile(self.target + 'etc/kdump.conf'):
            with open(self.target + 'etc/kdump.conf', 'r') as kfile:
                for line in kfile:
                    if not line.startswith("#") and not line.startswith('\n'):
                            kdumpConfig[line.split()[0]] = line.split(line.split()[0])[1].strip('\n')
        else:
            kdumpConfig['path'] = False
        
        if 'path' not in kdumpConfig:
            kdumpConfig['path'] = '/var/crash/'
        return kdumpConfig
        

    def getCrashInfo(self):
        
        crashInfo = {}
        try:
            crashInfo['memReserve'] = pysosutils.getCmdLine(self.target).split('crashkernel=')[1].split()[0]
        except IndexError:
            crashInfo['memReserve'] = 'Not Defined'
        
        crashInfo['path'] = self.getKdumpConfig()['path']
        if crashInfo['path']:
            fs = filesys.filesys(self.target)
            mounts = fs.getFsMounts()
            for mount in mounts:
                if mounts[mount]['mountPoint'] == crashInfo['path']:
                    crashInfo['pathFreeSpace'] = fs.getFsSize(mounts[mount]['mountPoint'])['avail']
                    crashInfo['pathDevice'] = mounts[mount]['dev']
            # hit this if there is no explicit mount point for the crashpath. Assume root fs.
            if 'pathFreeSpace' not in crashInfo:
                crashInfo['pathFreeSpace'] = int(fs.getFsSize('/')['avail']) / 1048576
                crashInfo['pathDevice'] = fs.getFsDev('/')
        else:
            crashInfo['path'] = 'No kdump.conf file found'
            crashInfo['pathDevice'] = 'device unknown'
            crashInfo['pathFreeSpace'] = 'Unknown'
        
        mem = memory.memory(self.target)
        crashInfo['memRequired'] = int(mem.getMemInfo()['total'])
        return crashInfo

    def displayKernelInfo(self):
        kernel = pysosutils.getKernelVersion(self.target)
        kdumpVer = self.getKdumpVersion()[0]
        kdumpState = self.getKdumpState()
        kdumpConfig = self.getKdumpConfig()
        panicSysctls = pysosutils.getSysctl(self.target, 'panic')
        crashInfo = self.getCrashInfo()
        taintCodes = pysosutils.getTaintCodes(self.target)

        print colors.SECTION + colors.BOLD + 'Kernel ' + colors.ENDC
        print colors.HEADER_BOLD + '\t Running Kernel      :  ' + colors.ENDC + kernel
        print colors.HEADER_BOLD + '\t Kernel Taint State  : ' + colors.ENDC + taintCodes[0]
        if len(taintCodes) > 1:
            taintCodes.pop(0)
            for item in taintCodes:
                print '\t\t\t       ' + item
        print colors.HEADER_BOLD + '\t kexec-tools version :  ' + colors.ENDC + kdumpVer
        print colors.HEADER_BOLD + '\t Service enablement  :  ' + colors.ENDC + kdumpState
        print colors.HEADER_BOLD + '\t Memory Reservation  :  ' + colors.ENDC + crashInfo['memReserve']
        
        print ''
        print colors.HEADER_BOLD + '\t kdump.conf          : ' + colors.ENDC
        for key in kdumpConfig:
            if kdumpConfig[key]:
                print '\t\t\t\t%s  %s' %(key, kdumpConfig[key])
        print colors.BLUE + colors.BOLD + '\t\t Crash Path   : ' + colors.ENDC + crashInfo['path'] + '  ({})'.format(crashInfo['pathDevice'])
        print colors.BLUE + colors.BOLD + '\t\t Space Needed : ' + colors.ENDC + '{:>6.2f} GB'.format(math.ceil(float(crashInfo['memRequired']) / 1000))
        
        if type(crashInfo['pathFreeSpace']) is int:
            print colors.BLUE + colors.BOLD + '\t\t Free Space   : ' + colors.ENDC + '{:>6.2f} GB'.format(crashInfo['pathFreeSpace'])
        else:
            print colors.BLUE + colors.BOLD + '\t\t Free Space   : ' + colors.ENDC + 'Unknown'


        if crashInfo['memRequired'] / 1000 > crashInfo['pathFreeSpace']:
            print '\t\t\t ' + colors.WARN + 'NOT ENOUGH SPACE FOR VMCORE DUMP' + colors.ENDC

        
        print ''

        print colors.HEADER_BOLD + '\t Kernel Panic Sysctl : ' + colors.ENDC
        for item in panicSysctls:
            if panicSysctls[item] == '0':
                ctl = ' = 0 ' + '[disabled]' + colors.ENDC
            elif panicSysctls[item] == '1':
                ctl = ' = 1 ' + colors.BOLD + '[enabled]' + colors.ENDC
            else:
                ctl = ' = %s ' %item.split()[2]
            print '\t\t\t\t {:<31} {}'.format(item, ctl)
    
    
if __name__ == '__main__':
    target = sys.argv[1]
    test = kernel(target)
    test.displayKernelInfo()
