import sys, os, pysosutils, math
from colors import *

class network():

    def __init__(self, target, vnetDisplay=False, vlanDisplay=False):
        self.target = target
        self.vnetDisplay = vnetDisplay
        self.vlanDisplay = vlanDisplay
        self.devList = self.getIntList()

    def _setLineColor(self, dev):
        if 'eth' in dev or 'em' in dev or 'enp' in dev or dev.startswith('p'):
            return colors.BLUE
        elif 'vlan' in dev:
            return colors.CYAN
        elif 'bond' in dev:
            return colors.GREEN
        elif 'vnet' in dev:
            return colors.WHITE
        else:
            return colors.PURPLE

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
                dev = str(line[0:index]).strip().lower()
                if devFilter:
                    if devFilter in dev:
                        devList.append(dev)
                else:
                    if not 'vnet' in dev and not 'vlan' in dev:
                        devList.append(dev)
                    else:
                        if self.vnetDisplay:
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
        devInfo = {}
        for dev in self.devList:
            if not '.' in dev:
                devInfo[dev] = self.getInterfaceInfo(dev)
                try:
                    if "Unknown!" in devInfo[dev]['Speed']:
                        devInfo[dev]['Speed'] = '{:^11}'.format('Unknown')
                    else:
                        devInfo[dev]['Speed'] = devInfo[dev]['Speed'].split('M')[0]
                except KeyError:
                    devInfo[dev]['Speed'] = ''
                    devInfo[dev]['Auto-negotiation'] = ''
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

        # if that fails, go for ip_address which may or may not be present
        if os.path.isfile(self.target + 'sos_commands/networking/ip_address'):
            with open(self.target + 'sos_commands/networking/ip_address', 'r') as ifile:
                for n, line in enumerate(ifile):
                    if device in line:
                        for i in range(3):
                            line = ifile.next()
                            if 'inet ' in line:
                                return line[line.find('inet')+4:line.find('/')-1].strip()
                        

        # if we reach this point, we can't reliably determine the IP address, and return an empty string
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
                        # Depending on the OS version, there may or may not be a space between the device name
                        # and the number of bytes received. What we do here is check for that, and adjust line[0]
                        # appropriately so that the dictionary can be defined the same regardless.
                        if line[0].strip(':') == device:
                            line.pop(0)
                        else:
                            line[0] = line[0].split(':')[1]
                        line = map(int, line)
                        netStats= {'rxBytes': line[0], 'rxPkts': line[1], 'rxErrs': line[2],\
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
        try:
            if 'yes' in devSettings['Link detected']:
                devSettings['Link detected'] = 'UP'
            else:
                devSettings['Link detected'] = 'DOWN'
        except:
            pass
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
                if 'Operation not supported' in rfile.readline():
                    return { 'maxRx': '?', 'maxTx': '?', 'currentRx': '?', 'currentTx': '?' }
                # easiest way to parse this is by line number since it's a fixed output
                for i, line in enumerate(rfile.readlines()):
                    if i == 1:
                        ringSettings['maxRx'] = line.split()[1].strip()
                    elif i == 4:
                        ringSettings['maxTx'] = line.split()[1].strip()
                    elif i == 6:
                        ringSettings['currentRx'] = line.split()[1].strip()
                    elif i == 9:
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
        print colors.WHITE + colors.BOLD + '\t {:^10}    {:^20}  {:^8}  {:^15}{:^15}'.format(\
        'Device', 'Link', 'Auto-Neg', 'Ring R/T', 'Driver Info')
        print '\t ' + '=' * 10 + '\t ' + '=' * 17 + '  ' + '=' * 10 + '\t ' + '=' * 10 + '   ' + '=' * 15 + colors.ENDC
        for item in sorted(devInfo):
            try:
                value = devInfo[item]
                linecolor = self._setLineColor(item)
                print '\t' + linecolor + '  {:^7}'.format(item) + '\t{:>5}'.format(value['Link detected'].upper())\
                 + '{:^10} '.format(value['Speed']) + '\t{:^4}'.format(value['Auto-negotiation'].upper())\
                 + '\t {:>4}/{:<4}'.format(value['currentRx'], value['currentTx'])\
                 + '   {:<7}{:<10} fw:{:8}'.format(value['driver'], value['driverVersion'], value['firmware']) + colors.ENDC
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
        devInfo = {}
        for dev in self.devList:
            devInfo[dev] = self.getIfcfgInfo(dev)
            if devInfo[dev]:
                devInfo[dev]['ipAddr'] = self.getIpAddr(dev)
                devInfo[dev]['macAddr'] = self.getMacAddr(dev)
            else:
                del devInfo[dev]
        print colors.SECTION + colors.BOLD + 'IP Info' + colors.ENDC
        print colors.WHITE + '\t   Device\t     IP Addr\t     Member Of\t     MTU\t      HW Addr' + colors.ENDC
        print colors.WHITE + '\t ' + '=' * 10 + ' ' * 6 + '=' * 15 + ' ' * 4 + '=' * 11 + ' ' * 5 + '=' * 5 + '\t' + '=' * 19 + colors.ENDC
        for dev in sorted(devInfo):
            linecolor = self._setLineColor(dev)
            print linecolor + '\t {:^10}\t {:^15}     {:^10}\t    {:^5} \t {:<5}'.format(dev, devInfo[dev]['ipAddr'], devInfo[dev]['master'], devInfo[dev]['mtu'], devInfo[dev]['macAddr']) + colors.ENDC


    def displayNetDevInfo(self):
        netStats = {}
        for dev in self.devList:
            netStats[dev] = self.getNetDevInfo(dev)
            if netStats[dev] == False:
                del netStats[dev]
        print colors.SECTION + colors.BOLD + 'NetDev Stats' + colors.ENDC
        print colors.WHITE + '\t   Device      RxGbytes      RxPkts      RxErrs     RxDrops     TxGbytes     TxPkts    '+ \
        ' TxErrs    TxDrops' + colors.ENDC
        print colors.WHITE + '\t '+'='* 10 + '   ' + '=' * 10 + '   ' + '=' * 9 + '   ' + '=' * 9 + '   ' + '=' * 9 + '   ' + '=' * 10 \
        + '  ' + '=' * 9 + '   ' + '=' * 8 + '  ' + '=' * 9 + colors.ENDC
        for dev in sorted(netStats):
            linecolor = self._setLineColor(dev)
            try:
                print linecolor + '\t {:^10}     {:>7.2f}\t    {:^5}m     {:>5}         {:>4}   \t{:>7.2f}     {:^5}m     {:>5}\t {:>4}'\
                .format(dev, math.ceil(float(netStats[dev]['rxBytes']) / 1024 / 1024 / 1024), (netStats[dev]['rxPkts'] / 1000 / 1000),\
                 netStats[dev]['rxErrs'], netStats[dev]['rxDrop'], math.ceil(float(netStats[dev]['txBytes']) / 1024 / 1024 / 1024),\
                 (netStats[dev]['txPkts'] / 1000 / 1000), netStats[dev]['txErrs'], netStats[dev]['txDrop']) + colors.ENDC  
            except:
                pass
    def displayAllNetInfo(self):
        if self.devList:
            self.displayEthtoolInfo()
            self.displayIpInfo()
            self.displayBondInfo()
            self.displayNetDevInfo()
        else:
            print colors.RED + colors.BOLD + 'Could not parse interface information' + colors.ENDC

if __name__ == '__main__':
    target = sys.argv[1]
    test = network(target)
    test.displayAllNetInfo()
