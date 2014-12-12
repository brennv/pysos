import sys, os, pysosutils
from colors import *

class network():

    def __init__(self, target):
        self.target = target


    def getIntList(self, devFilter=False):
        devList = []
        with open(self.target +'proc/net/dev', 'r') as dfile:
            lines = dfile.readlines()
            # the 'Iter-' and '-face' lines from the head of proc/net/dev
            # will get captured by this. Delete them from the list
            # There has to be a better way to do this
            lines.pop(0)
            lines.pop(0)
            for line in lines:
                index = line.find(':')
                dev = str(line[0:index]).strip()
                if devFilter:
                    if devFilter in dev:
                        devList.append(dev)
                else:
                    devList.append(dev)
        # we don't care about these devices
        try:
            devList.remove('lo')
            devList.remove(';vdsmdummy;')
        except:
            pass
        return devList


    def getInterfaceInfo(self, device):
        devSettings = {}
        try:
            devSettings.update(self.getEthtoolInfo(device))
            devSettings.update(self.getIntDriverInfo(device))
            devSettings.update(self.getRingInfo(device))
        except:
            pass

        return devSettings


    def getAllIntInfo(self):
        devList = self.getIntList()
        devInfo = {}
        for dev in devList:
            devInfo[dev] = self.getInterfaceInfo(dev)
            try:
                if "Unknown!" in devInfo[dev]['Speed']:
                    devInfo[dev]['Speed'] = '{:^11}'.format('Unknown')
                else:
                    devInfo[dev]['Speed'] = '{:6} Mb/s'.format(devInfo[dev]['Speed'].split('M')[0])
            except:
                pass
        checks = ['currentRx', 'currentTx', 'Speed']
        for check in checks:
            if check not in devInfo:
                devInfo[check] = ''
        return devInfo


    def getMacAddr(self, device):
        # first try the ifcfg-* file
        if os.path.isfile(self.target + 'etc/sysconfig/network-scripts/ifcfg-' + device):
            with open(self.target + 'etc/sysconfig/network-scripts/ifcfg-' + device, 'r') as ifile:
                for line in ifile.readlines():
                    if line.startswith('HWADDR'):
                        return line[line.find('=')+1:len(line)].replace('"', '').replace("'", '').strip('\n')
        # then default to ifconfig - though this will cause duplicate MACs with most bond modes
        if os.path.isfile(self.target + 'sos_commands/networking/ifconfig_-a'):
            with open(self.target + 'sos_commands/networking/ifconfig_-a', 'r') as ifile:
                for line in ifile:
                    if line[0].isalpha():
                        if line.split()[0] == device:
                            return line[line.find('HWaddr')+7:len(line)].strip('\n')
        else:
            return 'Not Found'


    def getIpAddr(self, device):
        # first try the ifcfg-* file
        if os.path.isfile(self.target + 'etc/sysconfig/network-scripts/ifcfg-' + device):
            with open(self.target + 'etc/sysconfig/network-scripts/ifcfg-' + device, 'r') as ifile:
                for line in ifile.readlines():
                    if line.startswith('IPADDR='):
                        return line[line.find('=')+1:len(line)].replace('"', '').replace("'", '').strip('\n')
        # if that fails, go to ifconfig -a
        if os.path.isfile(self.target + 'sos_commands/networking/ifconfig_-a'):
            devInfo = pysosutils.parseOutputSection(self.target + 'sos_commands/networking/ifconfig_-a', device)
            try:
                if devInfo['inet addr']:
                    return devInfo['inet addr']
            except KeyError:
                return ''
        
        return ''


    def getIfcfgInfo(self, device):
        if os.path.isfile(self.target + 'etc/sysconfig/network-scripts/ifcfg-' + device):
            ifcfgInfo = {}
            with open(self.target + 'etc/sysconfig/network-scripts/ifcfg-' + device, 'r') as ifile:
                 for line in ifile.readlines():
                     if line.startswith('MASTER'):
                         ifcfgInfo['master'] = line[line.find('=')+1:len(line)].replace('"', '').replace("'", '').strip('\n')
                     elif line.startswith('MTU'):
                         ifcfgInfo['mtu'] = line[line.find('=')+1:len(line)].replace('"', '').replace("'", '').strip('\n')
                     elif line.startswith('BRIDGE'):
                         ifcfgInfo['master'] = line[line.find('=')+1:len(line)].replace('"', '').replace("'", '').strip('\n')
            if not 'mtu' in ifcfgInfo:
                ifcfgInfo['mtu'] = 1500
            if not 'master' in ifcfgInfo:
                ifcfgInfo['master'] = ''
            return ifcfgInfo
        else:
            return False


    def getNetDevInfo(self, device):
        if os.path.isfile(self.target + 'proc/net/dev'):
            netStats = {}
            with open(self.target + 'proc/net/dev', 'r') as nfile:
                for line in nfile.readlines():
                    if line.split(':')[0].strip() == device:
                        line = line.split()
                        netStats= {'rxBytes': line[0].split(':')[1], 'rxPkts': line[1], 'rxErrs': line[2],\
                            'rxDrop': line[3], 'rxFifo': line[4], 'rxFrame': line[5], 'rxComprsd': line[6], \
                            'rxMulti': line[7], 'txBytes': line[8], 'txPkts': line[9], 'txErrs': line[10],\
                            'txDrop': line[11], 'txFifo': line[12],  'txColls': line[13], 'txCarrier': line[14],\
                            'txComprsd': line[15]}
                        if netStats['rxBytes'] == '':
                            netStats['rxBytes'] = 0
            return netStats
        else:
            return False

    def getBondInfo(self):
        bonds = self.getIntList(devFilter='bond')
        bondInfo = {}
        for bond in bonds:
            bondInfo[bond] = self.getBondIntInfo(bond)
            if os.path.isfile(self.target + 'etc/sysconfig/network-scripts/ifcfg-'+ bond):
                with open(self.target + 'etc/sysconfig/network-scripts/ifcfg-'+ bond, 'r') as bfile:
                    for line in bfile.readlines():
                        if line.startswith('BONDING_OPTS'):
                            bondInfo[bond]['bondingOpts'] = line[line.find('=')+1:len(line)].replace('"', '').replace("'", '').strip('\n')
                            break
        return bondInfo



    def getBondIntInfo(self, bond):
        bondInfo = {}
        bondInfo['slaves'] = []
        bondInfo['failures'] = []
        bondInfo['macAddrs'] = []
        if os.path.isfile(self.target + 'proc/net/bonding/' + bond):
            with open(self.target + 'proc/net/bonding/' + bond, 'r') as bfile:
                for line in bfile.readlines():
                    if line.startswith('Bonding Mode:'):
                        mode = line[line.find(':')+2:len(line)].strip('\n')
                        if 'IEEE 802.3ad' in mode:
                            mode = '802.3ad (LACP)'
                        bondInfo['mode'] = mode
                    elif line.startswith('Primary Slave'):
                         bondInfo['primary']= line[line.find(':')+2:len(line)].strip('\n')
                    elif line.startswith('Currently Active Slave:'):
                        bondInfo['active'] = line[line.find(':')+2:len(line)].strip('\n')
                    elif line.startswith('Slave Interface:'):
                        slave = line[line.find(':')+2:len(line)].strip('\n')
                        try:
                            if slave == bondInfo['active']:
                                slave = slave + '*'
                        except:
                            pass
                        bondInfo['slaves'].append(slave)
                    elif line.startswith('Link Failure Count:'):
                        bondInfo['failures'].append(line[line.find(':')+2:len(line)].strip('\n'))
                    elif line.startswith('Permanent HW addr:'):
                        bondInfo['macAddrs'].append(line[line.find(':')+2:len(line)].strip('\n'))
        return bondInfo



    def getEthtoolInfo(self, device):
        if os.path.isfile(self.target +  'sos_commands/networking/ethtool_' + device):
            devSettings = pysosutils.parseOutputSection(self.target+\
                'sos_commands/networking/ethtool_' + device, 'Settings')
        else:
            return False
        return devSettings


    def getIntDriverInfo(self, device):
        driverSettings = {}
        if os.path.isfile(self.target + 'sos_commands/networking/ethtool_-i_' + device):
            with open(self.target + 'sos_commands/networking/ethtool_-i_' + device, 'r') as efile:
                for line in efile:
                    if line.startswith('driver'):
                        driverSettings['driver'] = line.split(':')[1].strip('\n')
                    elif line.startswith('version'):
                        driverSettings['driverVersion'] = line.split(':')[1].strip('\n')
                    elif line.startswith('firmware-version'):
                        driverSettings['firmware'] = line.split(':')[1].strip('\n')
                    else:
                        break
        else:
            driverSettings['driver'] = '?'
            driverSettings['driverVersion'] = '?'
            driverSettings['firmware'] = '?'

        return driverSettings


    def getRingInfo(self, device):
        ringSettings = {}
        if os.path.isfile(self.target + 'sos_commands/networking/ethtool_-g_' + device):
            if 'bond' in device or 'vnet' in device:
                return {'maxRx': '?', 'maxTx': '?', 'currentRx': '?', 'currentTx': '?'}
            with open(self.target + 'sos_commands/networking/ethtool_-g_' + device, 'r') as rfile:
                # easiest way to parse this is by line number since it's a fixed output
                for i, line in enumerate(rfile.readlines()):
                    if i == 2:
                        ringSettings['maxRx'] = line.split()[1]
                    elif i == 5:
                        ringSettings['maxTx'] = line.split()[1]
                    elif i == 7:
                        ringSettings['currentRx'] = line.split()[1].strip()
                    elif i == 10:
                        ringSettings['currentTx'] = line.split()[1].strip()
            return ringSettings
        else:
            return {'maxRx': '?', 'maxTx': '?', 'currentRx': '?', 'currentTx': '?'}


    def displayEthtoolInfo(self):
        devInfo = self.getAllIntInfo()
        # remove invalid devices that ethtool either cannot run against
        # or are VLANs that ethtool only gets a link detected state for
        # Since we are looking for physical interfaces here we accept VLAN
        # interfaces being removed
        devInfo = dict((k, v) for k, v in devInfo.iteritems() if v)
        print colors.SECTION + colors.BOLD +  'Ethtool' + colors.ENDC
        print colors.WHITE + colors.BOLD + '\t {:^10}    {:^20}  {:^8}  {:^15}   {:^15}'.format(\
        'Device', 'Link', 'Auto-Neg', 'Ring R/T', 'Driver Info')
        print '\t ' + '=' * 10 + '\t ' + '=' * 17 + '  ' + '=' * 10 + '\t ' + '=' * 10 + '\t ' + '=' * 15 + colors.ENDC
        for item in sorted(devInfo):
            if ';' not in item:
                try:
                    value = devInfo[item]
                    if 'bond' in item:
                        linecolor = colors.GREEN
                    elif 'eth' in item or 'em' in item:
                        linecolor = colors.BLUE
                    else:
                        linecolor = colors.PURPLE
                    print '\t' + linecolor + item + '\t\t ' + '{:<5}'.format(value['Link detected'].upper())\
                     + '{}'.format(value['Speed']) + '  {:>3}'.format(value['Auto-negotiation'].upper())\
                     + '\t\t {:4}/{:4}'.format(value['currentRx'], value['currentTx'])\
                     + '\t' + '{:<10} '.format(value['driver']) + 'ver:{:8} fw:{:8}'.format(value['driverVersion'], value['firmware']) + colors.ENDC
                except:
                    pass


    def displayBondInfo(self):
        bondInfo = self.getBondInfo()

        print colors.SECTION + colors.BOLD + 'Bonding' + colors.ENDC
        print colors.WHITE + colors.BOLD + '\t {:^10}    {:^20}    {:^30}{:^31}'.format('Device', 'Mode', 'Slave Interfaces', 'Bonding Opts')
        print '\t ' + '=' * 10 + '\t' + '=' * 19 + '\t  ' + '=' * 25 + '\t' + '=' * 24 + colors.ENDC

        for bond in sorted(bondInfo):
            try:
                print colors.GREEN + '\t {:<10}'.format(bond) + colors.ENDC + '     {:^20}'.format(bondInfo[bond]['mode'])\
                 + '\t   {:6}{:<6}'.format(bondInfo[bond]['slaves'][0], bondInfo[bond]['macAddrs'][0])\
                 + '\t{}'.format(bondInfo[bond]['bondingOpts'])

                bondInfo[bond]['slaves'].pop(0)
                bondInfo[bond]['macAddrs'].pop(0)
                for i in range(len(bondInfo[bond]['slaves'])):
                    print '{:<51}{:6}{:<10}'.format(' ', bondInfo[bond]['slaves'][i], bondInfo[bond]['macAddrs'][i])
            except:
                pass


    def displayIpInfo(self):
        devList = self.getIntList()
        devInfo = {}
        for dev in devList:
            devInfo[dev] = self.getIfcfgInfo(dev)
            if devInfo[dev]:
                devInfo[dev]['ipAddr'] = self.getIpAddr(dev)
                devInfo[dev]['macAddr'] = self.getMacAddr(dev)
            else:
                del devInfo[dev]
        print colors.SECTION + colors.BOLD + 'IP Info' + colors.ENDC
        print colors.WHITE + colors.BOLD + '\t {:^15}        {:^20}      {:^11}   {:^12} {:^24}'.format('INT','IP ADDR', 'MEMBER OF','MTU', ' HW ADDR')
        print '\t' + '=' * 16 + ' ' * 6 + '=' * 23 + ' ' * 4 + '=' * 13 + ' ' * 5 + '=' * 5 + '\t' + '=' * 19 + colors.ENDC
        for dev in sorted(devInfo):
            if 'eth' in dev or 'em' in dev:
                linecolor = colors.BLUE
            elif 'vlan' in dev:
                linecolor = colors.CYAN
            elif 'bond' in dev:
                linecolor = colors.GREEN
            elif 'vnet' in dev:
                linecolor = colors.WHITE
            else:
                linecolor = colors.PURPLE
            print '\t' + linecolor + '{:<15s}'.format(dev) + '{:^36s}{:<16s}{:<5} \t {:<5}'.format(devInfo[dev]['ipAddr'], devInfo[dev]['master'], devInfo[dev]['mtu'], devInfo[dev]['macAddr']) + colors.ENDC


    def displayNetDevInfo(self):
        devList = self.getIntList()
        netStats = {}
        for dev in devList:
            netStats[dev] = self.getNetDevInfo(dev)
            if netStats[dev] == False:
                del netStats[dev]
        print colors.SECTION + colors.BOLD + 'NetDev Stats' + colors.ENDC
        print colors.WHITE + '\t Int  \t\tRxGbytes     RxPkts      RxErrs     RxDrops     TxGbytes     TxPkts    '+ \
        ' TxErrs    TxDrops' + colors.ENDC
        print '\t'+'='* 12 + '   ' + '=' * 9 + '   ' + '=' * 9 + '   ' + '=' * 9 + '   ' + '=' * 9 + '   ' + '=' * 10 \
        + '  ' + '=' * 9 + '   ' + '=' * 8 + '  ' + '=' * 9
        for dev in sorted(netStats):
            if 'eth' in dev or 'em' in dev:
                linecolor = colors.BLUE
            elif 'vlan' in dev:
                linecolor = colors.CYAN
            elif 'bond' in dev:
                linecolor = colors.GREEN
            elif 'vnet' in dev:
                linecolor = colors.WHITE
            else:
                linecolor = colors.PURPLE

            print linecolor + '\t {:10}    {:>7.2f} \t   {:>5}m     {:>5}         {:>4}   \t {:>7.2f}   {:>5}m     {:>5}      {:>4}'\
            .format(dev, int(netStats[dev]['rxBytes']) / 1024 / 1024 / 1024, (int(netStats[dev]['rxPkts']) / 1000 / 1000),\
             netStats[dev]['rxErrs'], netStats[dev]['rxDrop'], int(netStats[dev]['txBytes']) / 1024 / 1024 / 1024,\
             (int(netStats[dev]['txPkts']) / 1000 / 1000), netStats[dev]['txErrs'], netStats[dev]['txDrop']) + colors.ENDC  

    def displayAllInfo(self):
        self.displayEthtoolInfo()
        self.displayIpInfo()
        self.displayBondInfo()
        self.displayNetDevInfo()

if __name__ == '__main__':
    target = sys.argv[1]
    test = network(target)
    test.displayAllInfo()
