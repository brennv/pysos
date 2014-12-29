import sys
import os
import pysosutils
import re
from colors import *

class Object(object):
    pass

class yum():
    """ 
    Capture and optionally display yum and subscription data
    for RPM based systems.
    
    Note that subscription information is RHEL specific.
    """

    def __init__(self, target):
        self.target = target
        self.plugins = ''

    def getLastUpdate(self):
        """ Get the last package updated """
        if os.path.isfile(self.target + 'var/log/yum.log'):
            with open(self.target + 'var/log/yum.log', 'r') as yfile:
                # this is horribly ineffecient. Need a better way.  
                lines = yfile.readlines()
                try:
                    return lines[-1]
                except IndexError:
                    return False

        else:
            return False

    def getLastUpdateDate(self):
        """ Get the last date an update was performed """
        lastUpdate = self.getLastUpdate()
        if lastUpdate:
            return lastUpdate[:15]
        else:
            return ' Unknown'

    def getRepoList(self):
        """ Compile a list of all repos the system is using """
        if os.path.isfile(
                    self.target + 'sos_commands/yum/yum_-C_repolist'):
            yumInfo = []
            with open(self.target + 'sos_commands/yum/yum_-C_repolist'\
                        , 'r') as yfile:
                for line in yfile:
                    if line.startswith('Loaded plugins:'):
                        self.plugins = line.split(':')[1].strip('\n')
                    elif not line.startswith('repo id') and not \
                             line.startswith('repolist:') and not \
                             line.startswith('This') and not \
                             line.startswith(' '):
                        repo = Object()
                        repo.repo = line.split()[0]
                        repo.name = line.strip(repo.repo).strip(
                                                    line.split()[-1])
                        yumInfo.append(repo)
            return yumInfo
        else:
            return False

    def getSubMgrInst(self):
        """ Get subscription information from subscription manager """
        if os.path.isfile(self.target + 
            'sos_commands/general/subscription-manager_list_--installed'):
            prodToParse = []
            prodInfo = []
            with open(self.target + 
                    'sos_commands/general/subscription-manager_list_--installed',
                    'r') as sfile:
                for line in sfile:
                    if line.startswith('Product Name:'):
                        prod = Object()
                        prod.header = line.strip('\n')
                        prodToParse.append(prod)
            for prod in prodToParse:
                 prod.data = pysosutils.parseOutputSection(
                    self.target + 
                    'sos_commands/general/subscription-manager_list_--installed',
                    prod.header)
                 for k in prod.data:
                     setattr(prod, str(k).lower().strip().replace(
                                                ' ', ''), prod.data[k])
                 prod.name = prod.header.replace('Product Name:',
                                                            '').strip()
                 prodInfo.append(prod)
            return prodInfo
        else:
            return False

    def displayYumInfo(self):
        """ Display gathered yum related information """
        yumInfo = self.getRepoList()
        lastUpdate = self.getLastUpdateDate()
        print colors.BSECTION + "Package Information"\
            + colors.ENDC
        print colors.BHEADER + '\t Plugins     : ' + colors.ENDC + \
            self.plugins

        if lastUpdate:
            print colors.BHEADER + '\t Last Update :  ' + \
                colors.ENDC + lastUpdate
        print colors.BHEADER + '\t Repos       : ' + colors.ENDC
        if yumInfo:
            for repo in yumInfo:
                print '\t\t\t' + repo.repo
        else:
            print '\t\t\t ' + colors.BRED + 'Repolist file not found'\
                    + colors.ENDC

    def displaySubInfo(self):
        """ Display subscription related information """
        prodInfo = self.getSubMgrInst()
        print ''
        if prodInfo:
            print colors.BHEADER + '\t Products    :  ' + \
                colors.ENDC + str(len(prodInfo))
            for prod in prodInfo:
                print '\t\t\t' + prod.name
                print '\t\t\t' + prod.version + ' ' + prod.arch
                if prod.status == 'Subscribed':
                    print '\t\t\tSubscribed until ' + prod.ends
                else:
                    print '\t\t\tStatus ' + prod.status
                print ''

    def displayAllYumInfo(self):
        self.displayYumInfo()
        self.displaySubInfo()

if __name__ == '__main__':
    target = sys.argv[1]
    test = yum(target)
    test.displayAllYumInfo()
