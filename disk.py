import sys
import os
from colors import *

class Object(object):
    pass

class disk:
    """ Capture and optionally display data on block devices """

    def __init__(self, target):
        self.target = target

    def _formatLunState(self, luns):
        """ 
        Given a list with the multipath state of a given LUN, format
        the state for display
        """
        if len(luns) == 1:
            state = luns[0].replace('[', '').replace(']', ' ').split()
            if 'active' in state[0]:
                state[0] = colors.BGREEN + 'active' + colors.ENDC
            else:
                state[0] = colors.RED + state[0] + colors.ENDC
            try:
                if 'ready' in state[1]:
                    state[1] = colors.BGREEN + state[1] + colors.ENDC
                else:
                    state[1] = colors.RED + state[1] + colors.ENDC
            except IndexError:
                pass
            state = ' '.join([x for x in state])
            return state

    def getBlockDevs(self):
        """ Get block devices on this system """
        if os.path.isfile(self.target +
                            'sos_commands/devicemapper/dmraid_-b'):
            devInfo = []
            with open(self.target +
                        'sos_commands/devicemapper/dmraid_-b',
                        'r') as dfile:
                for line in dfile:
                    dev = Object()
                    line = line.split()
                    dev.dev = line[0].split('/')[2].strip(':')
                    dev.size = line[1]
                    if 'dm-' not in dev.dev:
                        devInfo.append(dev)
            return devInfo
        else:
            return False

    def getMultiPathInfo(self):
        """ Parse multipath -ll for LUN and path data """
        if os.path.isfile(self.target +
                        'sos_commands/devicemapper/multipath_-v4_-ll'):
            mpathInfo = []
            with open(self.target +
                        'sos_commands/devicemapper/multipath_-v4_-ll', 
                        'r') as mfile:
                lines = mfile.readlines()
                for x in xrange(len(lines)):
                    line = lines[x]
                    if not line.startswith('mpath'):
                        pass
                    else:
                        dev = Object()
                        line = line.split()
                        dev.mpathDev = line[0]
                        dev.lun = line[1].strip('(').strip(')')
                        dev.dm = line[2]
                        dev.dType = line[3]
                        x += 1
                        line = lines[x].split()
                        dev.size = line[0].split('=')[1]
                        # dev.state = line[3].strip('[')
                        dev.lunDevs = []
                        dev.lunDevStats = []
                        x += 1
                        line = lines[x].split()
                        while True:
                            if len(line) == 4:
                                dev.pathType = line[1]
                            elif (len(line) >= 5 and len(line) <= 7):
                                for item in line:
                                    if 'sd' in item:
                                        dev.lunDevs.append(item)
                                        dev.lunDevStats.append(line[
                                                line.index(item)+2])
                            elif len(line) > 8:
                                break
                            try:
                                x += 1
                                line = lines[x].split()
                            except:
                                break
                        mpathInfo.append(dev)
            return mpathInfo
        else:
            return False

    def displayMultiPathInfo(self):
        devList = self.getBlockDevs()
        mpathInfo = self.getMultiPathInfo()
        print colors.BSECTION +\
                        'Disk and MultiPath Information' + colors.ENDC
        print ''
        print colors.BHEADER + '\t Block Devices  :' + colors.ENDC

        if devList:
            print colors.WHITE + '\t\t\t\t {:^8}\t {:^12}'.format(
                                    'Device', 'Size (GB)') + colors.ENDC
            print colors.WHITE + '\t\t\t\t ' + '=' * 8 + '\t ' +\
                                                '=' * 11 + colors.ENDC
            for dev in devList:
                print '\t\t\t\t {:>6}\t      {:>10}'.format(dev.dev, 
                                                int(dev.size) / 1048576)
        else:
            print ''
            print colors.RED + '\t\tBlock device information not found.'
        print ''
        print colors.BHEADER + '\t MultiPath Info :' + colors.ENDC
        print colors.WHITE +\
                '\t\t\t  {:^8}    {:^6}   {:^35}\t{:10}   {:10}'.format(
                        'Device', 'Size', 'LUN ID', 'DM Devs',
                        'Status') + colors.ENDC
        print colors.WHITE + '\t\t\t  ' + '=' * 8 + '   ' + '=' * 8 +\
                '  ' + '=' * 35 + '     ' + '=' * 9 + '  ' + '=' * 14 +\
                colors.ENDC
        for dev in sorted(mpathInfo):
            dmDevs = ' '.join([x for x in dev.lunDevs])
            lunState = self._formatLunState(list(set(dev.lunDevStats)))
            
            print '\t\t\t  {:^8}    {:>6}   {:^36} '.format(
                dev.mpathDev, dev.size, dev.lun) + '   {:^10}'.format(
                    dmDevs) + '  {:^10}'.format(lunState)

if __name__ == '__main__':
    target = sys.argv[1]
    test = disk(target)
    test.displayMultiPathInfo()
