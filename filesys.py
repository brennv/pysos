import sys, os, textwrap
from collections import OrderedDict
from colors import *

class filesys():
    
    def __init__(self, target, showFsOpts=False):
        self.target = target
        self.showFsOpts = showFsOpts


    def getFsMounts(self):
        if os.path.isfile(self.target + 'sos_commands/filesys/mount_-l'):
            mounts= OrderedDict()
            with open(self.target + 'sos_commands/filesys/mount_-l', 'r') as mfile:
                for line in mfile:
                    if line.startswith('cgroup'):
                        pass
                    else:
                        line2 = line.strip('\n').split()
                        try:
                            mounts[line2[0]] = {'dev': line2[0].lstrip('/dev/mapper'), 'mountPoint': line2[2], 'fsType': line2[4]\
                            , 'mountOpts': line[line.find('(')+1:line.find(')')-2].strip() }
                        except:
                            pass
            return mounts
        else:
            return False

    def getFsSize(self, mount):
        if os.path.isfile(self.target + 'sos_commands/filesys/df_-al'):
            mount = mount.strip()
            with open(self.target + 'sos_commands/filesys/df_-al', 'r') as mfile:
                for line in mfile:
                    line = line.split()
                    try:
                        if line[4] == mount or line[5] == mount:
                            if len(line) == 6:
                                line.pop(0)
                            percUsed = line[3].strip('%')
                            try:
                                percAvail = 100 - float(percUsed)
                            except:
                                percAvail = '-'
                            return {'size': int(line[0]), 'used': line[1], 'avail': line[2], 'percAvail': percAvail, 'percUsed': percUsed}
                    except:
                        pass
            return {'size': '', 'used': '', 'avail': '', 'percAvail': ''}

        else:
            return {'size': '', 'used': '', 'avail': '', 'percAvail': ''}

    def getFsDev(self, mount):
        if os.path.isfile(self.target + 'sos_commands/filesys/mount_-l'):
            with open(self.target + 'sos_commands/filesys/mount_-l', 'r') as mfile:
                for line in mfile:
                    if line.split()[2] == mount:
                        return line.split()[0]
            # if we don't hit anything, return that fact
            return 'Unknown Mount Device'
        else:
            return 'Cannot find mount file'
        

    def getAllMountInfo(self):
        mounts = self.getFsMounts()
        for mount in mounts:
            mounts[mount].update(self.getFsSize(mounts[mount]['mountPoint']))
        return mounts

    def displayFsInfo(self):
        mounts = self.getAllMountInfo()
        for key in mounts.keys():
            if mounts[key]['size'] < 1 or 'tmpfs' in mounts[key]['dev']:
                del mounts[key]
        print colors.SECTION + colors.BOLD + 'File System Information' + colors.ENDC
        print ''
        print colors.WHITE + '\t {:^30}\t {:^20}\t  {:^7}    {:^7}    {:^12}'.format('Device', 'Mount Point', 'Size', 'Used', 'Available') + colors.ENDC
        print colors.WHITE + '\t ' + '=' * 30 +'\t ' + '=' * 19 + '\t' + '=' * 9 + '  ' + '=' * 9 + '   ' + '=' * 14 + colors.ENDC
        for mount in mounts:
            try:
                mounts[mount]['size'] = float(mounts[mount]['size']) / 1048576
                mounts[mount]['used'] = float(mounts[mount]['used']) / 1048576
                mounts[mount]['avail'] = float(mounts[mount]['avail']) / 1048576
            except:
                pass
            try:
                print '\t {:<30}\t  {:<12} {:<6}   {:>6.2f} GB  {:>6.2f} GB   {:>6.2f} GB ({:^2}%)'.format(mounts[mount]['dev'], mounts[mount]['mountPoint']\
                    ,mounts[mount]['fsType'], mounts[mount]['size'], mounts[mount]['used'], mounts[mount]['avail'], mounts[mount]['percAvail'])
            except ValueError:
                print '\t {:<30}\t  {:<12} {:<6}'.format(mounts[mount]['dev'], mounts[mount]['mountPoint'], mounts[mount]['fsType'])
                
            if self.showFsOpts:
                print "\t\t " + u"\u2192" + textwrap.fill(mounts[mount]['mountOpts'], 90, subsequent_indent='\t\t  ')

if __name__ == '__main__':
    target = sys.argv[1]
    test = filesys(target)
    test.displayFsInfo()
