import sys
import pysosutils
import math
import ps
from colors import Color as c
from rhevm import rhevm


class Object(object):
    pass


class virt():

    def __init__(self, target):
        self.target = target
        self.pprint = c()

    def getVdsmVer(self):
        return pysosutils.getRpmVer(self.target, 'vdsm')

    def getSpiceVer(self):
        return pysosutils.getRpmVer(self.target, 'spice-server')

    def getLibVirtVer(self):
        return pysosutils.getRpmVer(self.target, 'libvirt')

    def getQemuKvm(self):
        if self.checkIsRhev():
            return pysosutils.getRpmVer(self.target, 'qemu-kvm-rhev')
        else:
            return pysosutils.getRpmVer(self.target, 'qemu-kvm')

    def getQemuImg(self):
        if self.checkIsRhev():
            return pysosutils.getRpmVer(self.target, 'qemu-img-rhev')
        else:
            return pysosutils.getRpmVer(self.target, 'qemu-img')

    def getRhevToolsVer(self):
        return pysosutils.getRpmVer(self.target, 'qemu-kvm-rhev-tools')

    def checkIsRhevm(self):
        return pysosutils.getRpm(self.target, 'rhevm', boolean=True)

    def checkIsRhev(self):
        return pysosutils.getRpm(self.target, 'vdsm', boolean=True)

    def checkHostedEngine(self):
        hosted = Object()
        if pysosutils.getRpm(self.target, 'ovirt-hosted-engine-ha',
                             boolean=True):
            hosted.hosted = True
            hosted.version = pysosutils.getRpmVer(self.target,
                                                  'ovirt-hosted-engine-ha')
            hosted.broker = self.getBrokerStatus()
            hosted.agent = self.getAgentStatus()
            hosted.host = 'Coming'
        else:
            hosted.hosted = False
        return hosted

    def getBrokerStatus(self):
        pass

    def getAgentStatus(self):
        pass

    def getHyperInfo(self):
        hyper = Object()
        hyper.rhev = self.checkIsRhev

        if hyper.rhev:
            hyper.vdsm = self.getVdsmVer()
            hyper.spice = self.getSpiceVer()
            hyper.tools = self.getRhevToolsVer()
            hyper.spm = self.checkSpm()
            hyper.hosted = self.checkHostedEngine()

        hyper.qemukvm = self.getQemuKvm()
        hyper.qemuimg = self.getQemuImg()
        hyper.libvirt = self.getLibVirtVer()

        return hyper

    def checkKvmCap(self):
        with open(self.target + 'sos_commands/kernel/lsmod',
                  'r') as lfile:
            for line in lfile:
                if ('kvm' in line or
                        'kvm_intel' in line or
                        'kvm_amd' in line):
                    return True
        return False

    def checkIsKvm(self):
        return pysosutils.getRpm(self.target, 'qemu-kvm', boolean=True)

    def showVirtPlat(self, db=False):
        self.pprint.bsection('Virtualization')
        if self.checkIsRhev():
            self.hyper = self.getHyperInfo()
            self.displayRhevInfo()
        elif self.checkIsRhevm():
            rhevMgr = rhevm(self.target, db=db)
            rhevMgr.displayRhevmInfo()
        elif self.checkIsKvm():
            self.displayKvmInfo()
        elif self.checkKvmCap():
            print '\tKVM capable but does not appear to be hypervisor'
        elif not self.checkKvmCap():
            print '\tSystem does not have any KVM modules loaded.'
        else:
            print "\tCouldn't determine virt capabilities."

    def getRunningVms(self):
        psObj = ps.procInfo(self.target)
        procs = psObj.parseProcFile()
        vms = []
        for proc in procs:
            if '/usr/libexec/qemu-kvm' in proc.command:
                proc.name = proc.command.split()[2]
                vms.append(proc)
        return vms

    def checkSpm(self):
        spm = pysosutils.fileToString(self.target +
                                      'sos_commands/vdsm/vdsClient_-s_0_getAllTasksStatuses')
        if 'Not SPM' in spm:
            return False
        else:
            return True

    def getVdsmStatus(self):
        return pysosutils.fileToString(self.target +
                                       'sos_commands/vdsm/etc.init.d.vdsmd_status')

    def displayHyperInfo(self):
        colors = c()
        try:
            self.hyper
        except:
            self.hyper = self.getHyperInfo()
        self.pprint.bheader('\t Release    : ',
                            pysosutils.getRelease(self.target)
                            )
        self.pprint.bheader('\t Kernel     : ',
                            pysosutils.getKernelVersion(self.target)
                            )
        print ''

        print colors.BLUE + '\t vdsm\t    : ' + colors.ENDC + '{:22}'\
            .format(self.hyper.vdsm) + colors.BLUE +\
            ' \t libvirt     : ' + colors.ENDC + '{:22}'.format(
                self.hyper.libvirt)

        print colors.BLUE + '\t qemu-img   : ' + colors.ENDC +\
            '{:22}'.format(self.hyper.qemuimg) + colors.BLUE +\
            ' \t qemu-kvm    : ' + colors.ENDC +\
            '{:22}'.format(self.hyper.qemukvm)

    def displayRhevInfo(self):
        self.displayHyperInfo()
        colors = c()
        print colors.BLUE + '\t SPICE\t    : ' + colors.ENDC +\
            '{:22}'.format(self.hyper.spice) + ' \t ' \
            + colors.BLUE + 'RHEV Tools  : ' + colors.ENDC\
            + '{:22}'.format(self.hyper.tools)
        print ''
        print colors.WHITE + '\t SPM Status : ' + colors.ENDC +\
            '{}'.format(self.hyper.spm) + colors.WHITE +\
            '\t Hosted Engine : ' + colors.ENDC + '{}'.format(
                self.hyper.hosted.hosted)
        print ''
        self.displayRunningVms()

    def displayKvmInfo(self):
        self.displayHyperInfo()
        self.displayRunningVms()

    def displayRunningVms(self):
        vms = self.getRunningVms()
        self.pprint.bheader('\t Running VMs on this host : ',
                            str(len(vms)),
                            '\t CPU/RSS GB usage in ()'
                            )
        for i in range(0, (len(vms) / 4) + 1):
            vmLine = '\t '
            for x in range(0, 4):
                try:
                    proc = vms[0]
                    vmInfo = ' {0:{1}} ({2:<{3}} /{4:>{5}})'.format(
                        proc.name[:15].strip('.'), 15, proc.cpu, 4,
                        int(math.ceil(float(proc.rss) / 1000 / 1000)), 3)
                    vms.pop(0)
                    vmLine += vmInfo
                except:
                    pass
            print vmLine
        print ''

if __name__ == '__main__':
    target = sys.argv[1]
    test = virt(target)
    test.showVirtPlat()
