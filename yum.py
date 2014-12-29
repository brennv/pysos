import sys
import os
import pysosutils
import re
from colors import *

class yum():
    
    def __init__(self, target):
        self.target = target

    def getLastUpdate(self):
        if os.path.isfile(self.target + 'var/log/yum.log'):
            with open(self.target + 'var/log/yum.log', 'r') as yfile:
                # this is horribly ineffecient. Need a better way.  
                lines = yfile.readlines()
                return lines[-1]

        else:
            return False

    def getLastUpdateDate(self):
        lastUpdate = self.getLastUpdate()
        return lastUpdate[:15]

    def getRepoList(self):
        if os.path.isfile(self.target + 'sos_commands/yum/yum_-C_repolist'):
            yumInfo = {}
            with open(self.target + 'sos_commands/yum/yum_-C_repolist'\
                        , 'r') as yfile:
                for line in yfile:
                    if line.startswith('Loaded plugins:'):
                        yumInfo['plugins'] = line.split(':')[1].strip('\n')
                    elif not line.startswith('repo id') and not \
                             line.startswith('repolist:') and not \
                             line.startswith('This') and not \
                             line.startswith(' '):
                        line = line.split()
                        repo = line[0]
                        repoName = line[1]
                        repoStatus = line[2]
                        yumInfo[repo] = {'repo': repo, 
                            'repoName': repoName, 'repoStatus': repoStatus}
            return yumInfo
        else:
            return False

    def getSubMgrInst(self):
        if os.path.isfile(self.target + 
                'sos_commands/yum/subscription-manager_list_--installed'):
            prodToParse = []
            prodInfo = {}
            with open(self.target + 
                    'sos_commands/yum/subscription-manager_list_--installed',
                    'r') as sfile:
                for line in sfile:
                    if line.startswith('Product Name:'):
                        prodToParse.append(line.strip('\n'))
            for item in prodToParse:
                prodInfo[item.strip('Product Name:')] = pysosutils.parseOutputSection(
                    self.target + 
                    'sos_commands/yum/subscription-manager_list_--installed',
                    item)
            return prodInfo
        else:
            return False

    def displayYumInfo(self):
        yumInfo = self.getRepoList()
        prodInfo = self.getSubMgrInst()
        lastUpdate = self.getLastUpdateDate()
        print colors.BSECTION + "Package Information"\
            + colors.ENDC
        print colors.BHEADER + '\t Plugins     : ' + colors.ENDC + \
            yumInfo['plugins']
        del yumInfo['plugins']
        if lastUpdate:
            print colors.BHEADER + '\t Last Update :  ' + \
                colors.ENDC + lastUpdate
        print colors.BHEADER + '\t Repos       : ' + colors.ENDC
        for repo in yumInfo:
            print '\t\t\t' + yumInfo[repo]['repo']

        print ''
        if prodInfo:
            print colors.BHEADER + '\t Products    :  ' + \
                colors.ENDC + str(len(prodInfo))
            for prod in prodInfo:
                print '\t\t\t' + prod
                print '\t\t\t' + prodInfo[prod]['Version'] + ' ' + \
                    prodInfo[prod]['Arch']
                if prodInfo[prod]['Status'] == 'Subscribed':
                    print '\t\t\tSubscribed until ' + prodInfo[prod]['Ends']
                else:
                    print '\t\t\t' + prodInfo[prod]['Status']
                print ''



if __name__ == '__main__':
    target = sys.argv[1]
    test = yum(target)
    test.displayYumInfo()
