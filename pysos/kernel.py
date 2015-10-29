import sys
import os
from . import pysosutils
from . import opsys
from . import filesys
from . import memory
import math
from .colors import Color as c


class Object(object):
    pass


class kernel:

    """ Capture and optionally display kernel and dump data """

    def __init__(self, target):
        self.target = target
        self.pprint = c()

    def getKdumpState(self):
        """ Get chkconfig state of kdump service """
        return pysosutils.getChkConfig(self.target, 'kdump')

    def getKdumpVersion(self):
        """ Get version of kdump installed """
        return pysosutils.getRpm(self.target, 'kexec-tools')

    def getKdumpConfig(self):
        """ Get all config settings for kdump """
        kdump = {}
        if os.path.isfile(self.target + 'etc/kdump.conf'):
            with open(self.target + 'etc/kdump.conf', 'r') as kfile:
                for line in kfile:
                    if (not line.startswith("#") and not
                            line.startswith('\n')):
                        kdump[line.split()[0]] = (line.split(
                            line.split()[0])[1].strip('\n'))
        else:
            kdump = False
        return kdump

    def getCrashInfo(self):
        """ Get data related to the crashkernel memory reservation """
        crashInfo = Object()
        try:
            crashInfo.memreserve = pysosutils.getCmdLine(
                self.target).split('crashkernel=')[1].split()[0]
        except IndexError:
            crashInfo.memreserve = 'Not Defined'
        try:
            crashInfo.path = self.getKdumpConfig()['path']
        except:
            crashInfo.path = False
        if crashInfo.path:
            fs = filesys.filesys(self.target)
            mounts = fs.getFsMounts()
            for mount in mounts:
                try:
                    if mount.mountpoint == crashInfo.path.strip():
                        crashInfo.pathfreespace = fs.getFsSize(
                            mount.mountpoint).avail / 1048576
                        crashInfo.pathdevice = mount.dev
                except:
                    pass
            # Hit this if no explicit mount point for crashpath.
            # Assume root fs.
            if not hasattr(crashInfo, 'pathfreespace'):
                crashInfo.pathfreespace = int(fs.getFsSize('/').avail
                                              ) / 1048576
                crashInfo.pathdevice = fs.getFsDev('/')
        else:
            crashInfo.path = 'No kdump.conf file found'
            crashInfo.pathdevice = 'device unknown'
            crashInfo.pathfreespace = 'Unknown'

        mem = memory.memory(self.target)
        crashInfo.memrequired = int(mem.getMemInfo().total)
        return crashInfo

    def getAllKernelInfo(self):
        kernel = Object()
        kernel.booted = pysosutils.getKernelVersion(self.target)
        kernel.cmdline = pysosutils.getCmdLine(self.target)
        kernel.crash = self.getCrashInfo()
        kernel.kdumpconfig = self.getKdumpConfig()
        kernel.kdumpstate = self.getKdumpState()
        kernel.kdumpver = self.getKdumpVersion()
        kernel.panicsysctls = pysosutils.getSysctl(self.target, 'panic')
        return kernel

    def displayKernelInfo(self):
        """ Display kernel and kdump information """
        kernel = pysosutils.getKernelVersion(self.target)
        kdumpVer = self.getKdumpVersion()[0]
        kdumpState = self.getKdumpState()
        kdump = self.getKdumpConfig()
        panicSysctls = pysosutils.getSysctl(self.target, 'panic')
        crashInfo = self.getCrashInfo()
        taintCodes = pysosutils.getTaintCodes(self.target)

        self.pprint.bsection('Kernel ')
        self.pprint.bheader('\t Running Kernel     : ', kernel)
        self.pprint.bheader('\t Kernel Taint State  : ', taintCodes[0])
        if len(taintCodes) > 1:
            taintCodes.pop(0)
            for item in taintCodes:
                print('\t\t\t       ' + item)
        self.pprint.bheader('\t kexec-tools version :  ', kdumpVer)
        self.pprint.bheader('\t Service enablement  :  ', kdumpState)
        self.pprint.bheader('\t Memory Reservation  :  ',
                            crashInfo.memreserve
                            )

        print('')
        self.pprint.bheader('\t kdump.conf          : ')
        if kdump:
            for key in kdump:
                print('\t\t\t\t%s  %s' % (key, kdump[key]))
            self.pprint.bblue('\t\t Crash Path   : ',
                              crashInfo.path,
                              '  ({})'.format(
                                  crashInfo.pathdevice
                              )
                              )
            self.pprint.bblue('\t\t Space Needed : ',
                              '{:>6.2f} GB'.format(
                                  math.ceil(float(
                                      crashInfo.memrequired
                                  ) / 1000
                                  )
                              )
                              )

        else:
            self.pprint.bred('\t\t\t\t Unable to parse config')

        if type(crashInfo.pathfreespace) is int:
            self.pprint.bblue('\t\t Free Space   : ',
                              '{:>6.2f} GB'.format(
                                  crashInfo.pathfreespace
                              )
                              )
        else:
            self.pprint.bblue('\t\t Free Space   : ', 'Unknown')

        if crashInfo.memrequired / 1000 > crashInfo.pathfreespace:
            self.pprint.warn('\t\t\t\t NOT ENOUGH SPACE FOR VMCORE DUMP')
        print('')

        self.pprint.bheader('\t Kernel Panic Sysctl : ')
        colors = c()
        for item in panicSysctls:
            if panicSysctls[item] == '0':
                ctl = ' = 0 ' + '[disabled]' + colors.ENDC
            elif panicSysctls[item] == '1':
                ctl = ' = 1 ' + colors.BOLD + '[enabled]' + colors.ENDC
            else:
                ctl = ' = %s ' % panicSysctls[item]
            print('\t\t\t\t {:<31} {}'.format(item, ctl))

if __name__ == '__main__':
    target = sys.argv[1]
    test = kernel(target)
    test.displayKernelInfo()
