import sys
import os
import pysosutils
import math
from colors import *

class Object(object):
    pass

class network():
    """ Capture and optionally display network and interface data """

    def __init__(self, target, vnetDisplay=False, vlanDisplay=False):
        self.target = target
        self.vnetDisplay = vnetDisplay
        self.vlanDisplay = vlanDisplay
        self.devList = self.getIntList()

    def _setLineColor(self, dev):
        if ('eth' in dev or 'em' in dev or 'enp' in dev or 
                                                dev.startswith('p')):
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
        """ Get list of interfaces """
        devList = []
        with open(self.target +'proc/net/dev', 'r') as dfile:
            lines = dfile.readlines()
            # the 'Iter-' and '-face' lines from head of proc/net/dev
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
        """ Given a device, compile ethtool, driver and ring info """
        try:
            device = self.getEthtoolInfo(device = device)
            device = self.getIntDriverInfo(device = device)
            device = self.getRingInfo(device = device)
        except:
            pass
        return device

    def getAllIntInfo(self):
        """ Get all information for every interface in devList """
        devInfo = []
        for device in self.devList:
            dev = Object()
            if not '.' in device:
                dev.name = device
                dev = self.getInterfaceInfo(dev)
                try:
                    if "Unknown!" in dev.speed:
                        dev.speed = '{:^11}'.format('Unknown')
                    else:
                        dev.speed = dev.speed.split('M')[0]
                except:
                    pass
            devInfo.append(dev)
        return devInfo

    def getMacAddr(self, device):
        """ Get the MAC address for an interface """
        # first try the ifcfg-* file
        if os.path.isfile(self.target +
                    'etc/sysconfig/network-scripts/ifcfg-' + device):
            with open(self.target +
                    'etc/sysconfig/network-scripts/ifcfg-' + device,
                     'r') as ifile:
                for line in ifile.readlines():
                    if line.startswith('HWADDR'):
                        return line[line.find('=')+1:len(line)].replace(
                                '"', '').replace("'", '').strip('\n')
        # then default to ifconfig output file
        # though this will cause duplicate MACs with most bond modes
        if os.path.isfile(self.target +
                    'sos_commands/networking/ifconfig_-a'):
            with open(self.target +
                    'sos_commands/networking/ifconfig_-a',
                    'r') as ifile:
                for line in ifile:
                    if line[0].isalpha():
                        if line.split()[0] == device:
                            return line[line.find('HWaddr')+7:
                                                len(line)].strip('\n')
        else:
            return 'Not Found'

    def getIpAddr(self, device):
        """ Get the IP address for an interface """
        # first try the ifcfg-* file
        if os.path.isfile(self.target +
                    'etc/sysconfig/network-scripts/ifcfg-' + device):
            with open(self.target +
                    'etc/sysconfig/network-scripts/ifcfg-' + device,
                    'r') as ifile:
                for line in ifile.readlines():
                    if line.startswith('IPADDR='):
                        return line[line.find('=')+1:len(line)].replace(
                                '"', '').replace("'", '').strip('\n')
        # if that fails, go to ifconfig -a
        if os.path.isfile(self.target +
                    'sos_commands/networking/ifconfig_-a'):
            devInfo = pysosutils.parseOutputSection(self.target +
                    'sos_commands/networking/ifconfig_-a', device)
            try:
                if devInfo['inet addr']:
                    return devInfo['inet addr']
            except KeyError:
                return ''
        # if that fails try ip_address which may or may not be present
        if os.path.isfile(self.target +
                    'sos_commands/networking/ip_address'):
            with open(self.target +
                    'sos_commands/networking/ip_address', 'r') as ifile:
                for n, line in enumerate(ifile):
                    if device in line:
                        for i in range(3):
                            line = ifile.next()
                            if 'inet ' in line:
                                return line[line.find('inet')+4:
                                            line.find('/')-1].strip()
        # if we reach this point, we can't reliably determine the IP 
        return ''

    def getIfcfgInfo(self, dev):
        """ Get the ifcfg-file config settings for an interface """
        if not isinstance(dev, Object):
            name = device
            dev = Object()
            dev.name = name 

        if os.path.isfile(self.target +
                    'etc/sysconfig/network-scripts/ifcfg-' + dev.name):
            with open(self.target + 
                    'etc/sysconfig/network-scripts/ifcfg-' + dev.name,
                    'r') as ifile:
                 for line in ifile.readlines():
                     if line.startswith('MASTER'):
                         dev.master = line[line.find('=')+1:
                             len(line)].replace('"', '').replace(
                             "'", '').strip('\n')
                     elif line.startswith('MTU'):
                         dev.mtu = line[line.find('=')+1:
                             len(line)].replace('"', '').replace(
                             "'", '').strip('\n')
                     elif line.startswith('BRIDGE'):
                         dev.master = line[line.find('=')+1:
                             len(line)].replace('"', '').replace(
                             "'", '').strip('\n')
            try:
                dev.mtu
            except:
                dev.mtu = 1500

            try: 
                dev.master
            except:
                dev.master = ''
        else:
            dev = False

        return dev

    def getNetDevInfo(self, device):
        """ Get interface stats from /proc/net/dev """
        if os.path.isfile(self.target + 'proc/net/dev'):
            stats = ['rxbytes', 'rxpkts', 'rxerrs', 'rxdrop', 'rxfifo',
                'rxframe', 'rxcomprsd', 'rxmulti', 'txbytes', 'txpkts',
                'txerrs', 'txdrop', 'txfifo', 'txcolls', 'txcarrier',
                'txcomprsd']
            with open(self.target + 'proc/net/dev', 'r') as nfile:
                for line in nfile.readlines():
                    if line.split(':')[0].strip() == device:
                        dev = Object()
                        dev.name = device
                        line = line.split()
                        # Depending on the OS there may or may not be a
                        # space between the device name and the number
                        # of bytes received.
                        if line[0].strip(':') == device:
                            line.pop(0)
                        else:
                            line[0] = line[0].split(':')[1].strip()
                            if line[0] == '':
                                line.pop(0)
                        line = map(int, line)
                        x = 0
                        for stat in stats:
                            setattr(dev, stat, line[x])
                            x += 1
                        if dev.rxbytes == '':
                            dev.rxbytes = 0
            try:
                return dev
            except Exception as e:
                pass
        else:
            return False

    def getBondInfo(self):
        """ Get bonding ifcfg-file information for a bond interface """
        bonds = self.getIntList(devFilter='bond')
        bondInfo = []
        for bond in bonds:
            dev = self.getBondIntInfo(bond)
            if os.path.isfile(self.target +
                        'etc/sysconfig/network-scripts/ifcfg-'\
                        + bond):
                with open(self.target +
                        'etc/sysconfig/network-scripts/ifcfg-'\
                        + bond, 'r') as bfile:
                    for line in bfile.readlines():
                        if line.startswith('BONDING_OPTS'):
                            dev.bondingopts = line[line.find('=')+1:
                                len(line)].replace('"', '').replace(
                                "'", '').strip('\n')
                            break
            bondInfo.append(dev)
        return bondInfo

    def getBondIntInfo(self, bondDev):
        """ Get bond information from /proc/net/bonding/ """
        bond = Object()
        bond.name = bondDev
        bond.slaves = []
        bond.failures = []
        bond.macaddrs = []
        if os.path.isfile(self.target + 'proc/net/bonding/' + bond.name):
            with open(self.target + 'proc/net/bonding/' + bond.name,
                        'r') as bfile:
                for line in bfile.readlines():
                    if line.startswith('Bonding Mode:'):
                        mode = line[line.find(':')+2:
                                    line.find('(')-1].strip('\n')
                        if 'IEEE 802.3ad' in mode:
                            mode = '802.3ad (LACP)'
                        bond.mode = mode
                    elif line.startswith('Primary Slave'):
                         bond.primary= line[line.find(':')+2:
                                    len(line)].strip('\n')
                    elif line.startswith('Currently Active Slave:'):
                        bond.active = line[line.find(':')+2:
                                    len(line)].strip('\n')
                    elif line.startswith('Slave Interface:'):
                        slave = line[line.find(':')+2:
                                    len(line)].strip('\n')
                        try:
                            if slave == bond.active:
                                slave = slave + '*'
                        except:
                            pass
                        bond.slaves.append(slave)
                    elif line.startswith('Link Failure Count:'):
                        bond.failures.append(line[line.find(':')+2:
                                                len(line)].strip('\n'))
                    elif line.startswith('Permanent HW addr:'):
                        bond.macaddrs.append(line[
                                line.find(':')+2:len(line)].strip('\n'))
        return bond

    def getEthtoolInfo(self, device=False, devName=False):
        """ Get information as reported by ethtool for an interface """
        if not device:
            device = Object()
            device.name = devName
        if os.path.isfile(self.target +
                'sos_commands/networking/ethtool_' + device.name):
            devSettings = pysosutils.parseOutputSection(self.target +
                'sos_commands/networking/ethtool_' + device.name, 
                'Settings')
        else:
            return device
        try:
            if 'yes' in devSettings['Link detected']:
                devSettings['Link detected'] = 'UP'
            else:
                devSettings['Link detected'] = 'DOWN'
        except:
            pass

        for key, value in devSettings.items():
            setattr(device, 
                    key.replace(' ', '').replace('-', '').lower(),
                    value)
        
        try:
            device.speed
        except AttributeError:
            device.speed = ''
            device.autonegotiation = ''

        return device

    def getIntDriverInfo(self, device):
        """ Get driver information for an interface """
        if os.path.isfile(self.target +
                'sos_commands/networking/ethtool_-i_' + device.name):
            with open(self.target +
                'sos_commands/networking/ethtool_-i_' + device.name, 
                'r') as efile:
                for line in efile:
                    if line.startswith('driver'):
                        device.driver = line.split(':')[1].strip('\n')
                    elif line.startswith('version'):
                        device.driverversion = line.split(
                                                    ':')[1].strip('\n')
                    elif line.startswith('firmware-version'):
                        device.firmware = line.split(
                                                    ':')[1].strip('\n')
                    else:
                        break
        else:
            device.driver = ''
            device.driverVersion = ''
            device.firmware = ''
        return device

    def getRingInfo(self, device):
        """ Get ring information for an interface """
        if os.path.isfile(self.target +
                'sos_commands/networking/ethtool_-g_' + device.name):
            if 'bond' in device.name or 'vnet' in device.name:
                for item in ['maxrx', 'maxtx', 'currentrx',
                                'currenttx']:
                    setattr(device, item, '?')
                return device
            with open(self.target +
                'sos_commands/networking/ethtool_-g_' + device.name,
                'r') as rfile:
                if 'Operation not supported' in rfile.readline():
                    for item in ['maxrx', 'maxtx', 'currentrx',
                                'currenttx']:
                        setattr(device, item, '?')
                    return device
                # easiest way to parse this is by line number 
                # since it's a fixed output
                for i, line in enumerate(rfile.readlines()):
                    if i == 1:
                        device.maxrx = line.split()[1].strip()
                    elif i == 4:
                        device.maxtx = line.split()[1].strip()
                    elif i == 6:
                        device.currentrx = line.split()[1].strip()
                    elif i == 9:
                        device.currenttx = line.split()[1].strip()
            return device
        else:
            for item in ['maxrx', 'maxtx', 'currentrx', 'currenttx']:
                setattr(device, item, '?')
            return device

    def displayEthtoolInfo(self):
        """ Display formatted ethtool information for all devices """
        devInfo = self.getAllIntInfo()
        for dev in devInfo:
            try:
                if not dev.name:
                    devInfo.remove(dev)
            except KeyError or AttributeError:
                devInfo.remove(dev)
            except:
                pass
        print colors.BSECTION +  'Ethtool' + colors.ENDC
        print colors.WHITE + colors.BOLD +\
                    '\t {:^10}    {:^20}  {:^8}  {:^15}{:^15}'.format(
                    'Device', 'Link', 'Auto-Neg', 'Ring R/T', 
                    'Driver Info')
        # this is ugly, need to do this better
        print '\t ' + '=' * 10 + '\t ' + '=' * 17 + '  ' + '=' * 10 +\
                    '\t ' + '=' * 10 + '   ' + '=' * 15 + colors.ENDC
        for dev in devInfo:
            try:
                linecolor = self._setLineColor(dev.name)
                print '\t' + linecolor + '  {:^7}'.format(
                        dev.name) + '\t{:>5}'.format(
                        dev.linkdetected.upper()) + '{:^10} '.format(
                        dev.speed) + '\t{:^4}'.format(
                        dev.autonegotiation.upper()) +\
                        '\t {:>4}/{:<4}'.format(dev.currentrx,
                        dev.currenttx) +'   {:<7}{:<10} fw:{:8}'.format(
                        dev.driver, dev.driverversion, 
                        dev.firmware) + colors.ENDC
            except:
                pass

    def displayBondInfo(self):
        """ Display formatted bonding information for all bonds """
        bondInfo = self.getBondInfo()
        print colors.BSECTION + 'Bonding' + colors.ENDC
        print colors.WHITE + colors.BOLD +\
        '\t {:^10}    {:^20}    {:^30}{:^31}'.format('Device', 'Mode',
                                    'Slave Interfaces', 'Bonding Opts')
        print '\t ' + '=' * 10 + '\t' + '=' * 19 + '\t  ' + '=' * 25 +\
                                    '\t' + '=' * 24 + colors.ENDC
        for bond in sorted(bondInfo):
            try:
                print colors.GREEN + '\t {:<10}'.format(
                    bond.name) + colors.ENDC + '     {:^20}'.format(
                    bond.mode) + '\t   {:6}{:<6}'.format(bond.slaves[0],
                    bond.macaddrs[0]) + '\t{}'.format(bond.bondingopts)

                bond.slaves.pop(0)
                bond.macaddrs.pop(0)
                for i in range(len(bond.slaves)):
                    print '{:<51}{:6}{:<10}'.format(' ', bond.slaves[i],
                            bond.macaddrs[i])
            except:
                pass

    def displayIpInfo(self):
        """ Display formatted IP configuration for all devices """
        devInfo = []
        for device in self.devList:
            dev = Object()
            dev.name = device
            dev = self.getIfcfgInfo(dev)
            devInfo.append(dev)
            if dev:
                dev.ipaddr = self.getIpAddr(dev.name)
                dev.macaddr = self.getMacAddr(dev.name)
            else:
                devInfo.remove(dev)
        print colors.BSECTION + 'IP Info' + colors.ENDC
        print colors.WHITE +\
        '\t   Device\t     IP Addr\t     Member Of\t     MTU\t      HW Addr'\
        + colors.ENDC
        print colors.WHITE + '\t ' + '=' * 10 + ' ' * 6 + '=' * 15 +\
                        ' ' * 4 + '=' * 11 + ' ' * 5 + '=' * 5 + '\t' +\
                        '=' * 19 + colors.ENDC
        for dev in sorted(devInfo):
            linecolor = self._setLineColor(dev.name)
            print linecolor + \
            '\t {:^10}\t {:^15}     {:^10}\t    {:^5} \t {:<5}'.format(
            dev.name, dev.ipaddr, dev.master, dev.mtu, 
            dev.macaddr) + colors.ENDC

    def displayNetDevInfo(self):
        """ Display formatted /proc/net/dev stats for all devices """
        netStats = []
        for dev in self.devList:
            netStats.append(self.getNetDevInfo(dev))
        print colors.BSECTION + 'NetDev Stats'\
                + colors.ENDC
        print colors.WHITE + '\t   {}       {}     {}'.format(
            'Device', 'RxGbytes', 'RxPkts') + '\t {}\t    {}'.format(
            'RxErrs', 'RxDrops') + '\t{}     {}\t{}\t  {}'.format(
            'TxGbytes', 'TxPkts', 'TxErrs', 'TxDrops') + colors.ENDC
        print colors.WHITE + '\t '+'='* 10 + '   ' + '=' * 10 + '   ' +\
         '=' * 9 + '   ' + '=' * 9 + '   ' + '=' * 9 + '   ' + '=' * 10\
         + '   ' + '=' * 8 + '   ' + '=' * 8 + '  ' + '=' * 9 +\
         colors.ENDC
        for dev in sorted(netStats):
            linecolor = self._setLineColor(dev.name)
            try:
                print linecolor +\
                '\t {:^10}     {:>7.2f}\t    {:^5}m     {:>5}'.format(
                dev.name, math.ceil(float(dev.rxbytes)/ 1073741824),
                (dev.rxpkts / 1000000),
                dev.rxerrs) + '\t    {:>4}   \t{:>7.2f}'.format(
                dev.rxdrop, math.ceil(float(dev.txbytes) / 1073741824)
                ) + '\t     {:^5}m     {:^5}\t {:>4}'.format((dev.txpkts
                / 1000000), dev.txerrs, dev.txdrop) + colors.ENDC  
            except Exception as e:
                print e

    def displayAllNetInfo(self):
        """ Display ethtool, IP, bond and net stat information """
        if self.devList:
            self.displayEthtoolInfo()
            self.displayIpInfo()
            self.displayBondInfo()
            self.displayNetDevInfo()
        else:
            print colors.BRED +\
                'Could not parse interface information' + colors.ENDC

if __name__ == '__main__':
    target = sys.argv[1]
    test = network(target)
    test.displayAllNetInfo()
