import sys, os
from colors import *
class lspci():

    def __init__(self, target):
        self.target = target

    def getLspciInfo(self):
        if os.path.isfile(self.target + 'sos_commands/pci/lspci'):
            lspciInfo = {}
            with open(self.target + 'sos_commands/pci/lspci', 'r') as lfile:
                for line in lfile:
                    if 'lspci -nvv:' in line:
                        break
                    try:
                        pciAddr = line[0:line.find('.')-1]
                        if lspciInfo.has_key(pciAddr):
                            lspciInfo[pciAddr]['count'] += 1
                        else:
                            devType = line[line.find(pciAddr):line.find(': ')+1].strip(pciAddr).strip()
                            dev = line[line.find(': ')+2:len(line)].strip('\n')
                            if 'Ethernet' in devType:
                                devType = 'Ethernet'
                            elif 'VGA' in devType:
                                devType = 'VGA'
                            lspciInfo[pciAddr] = {'pciAddr': pciAddr, 'devType': devType, 'dev': dev, 'count': 1}
                    except:
                        pass
                
            return lspciInfo
        else:
            return False
            

    def displayLspciInfo(self, chkType):
        if not self.lspciInfo:
            self.lspciInfo = self.getLspciInfo()

        for key in self.lspciInfo:
            if chkType in lspciInfo[key]['devType']:
                if lspciInfo[key]['count'] > 1:
                    print colors.HEADER_BOLD + '\t\t {:10} : '.format(lspciInfo[key]['devType']) + colors.ENDC + colors.WHITE + '[{} ports]'.format(lspciInfo[key]['count']) + colors.ENDC +' {}'.format(lspciInfo[key]['dev'])
                else:
                    print colors.HEADER_BOLD + '\t\t {:10} : '.format(lspciInfo[key]['devType']) + colors.ENDC + ' {}'.format(lspciInfo[key]['dev'])


    def displayAllLspciInfo(self):
        self.lspciInfo = self.getLspciInfo()
        print colors.SECTION + colors.BOLD + 'LSPCI' + colors.ENDC
        if self.lspciInfo:
            print colors.HEADER_BOLD + '\t Physical Devices' + colors.ENDC
            # Not really *all*, just all we're interesting in
            self.displayLspciInfo('Ethernet')
            self.displayLspciInfo('Network')
            self.displayLspciInfo('IPMI')
            self.displayLspciInfo('VGA')
            self.displayLspciInfo('SCSI')
            self.displayLspciInfo('Serial Attached')
        else:
            print colors.RED + colors.BOLD + '\t LSPCI Information Not Found' + colors.ENDC


if __name__ == '__main__':
    target = sys.argv[1]
    test = lspci(target)
    test.displayAllLspciInfo()
                        
            
