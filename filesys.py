import sys, os, textwrap
from colors import *

class filesys():
    
    def __init__(self, target, showFsOpts=False):
        self.target = target
        self.showFsOpts = showFsOpts


    def getFsMounts(self):
        if os.path.isfile(self.target + 'sos_commands/filesys/mount_-l'):
            mounts= {}
            with open(self.target + 'sos_commands/filesys/mount_-l', 'r') as mfile:
                for line in mfile:
                    if line.startswith('cgroup'):
                        pass
                    else:
                        line2 = line.split()
                        mounts[line2[0]] = {'dev': line2[0].strip(), 'mountPoint': line2[2], 'fsType': line2[4]\
                        , 'mountOpts': line[line.find('(')+1:len(line)-2].strip() }
            return mounts
        else:
            return False

    def getFsSize(self, mount):
        if os.path.isfile(self.target + 'sos_commands/filesys/df_-al'):
            with open(self.target + 'sos_commands/filesys/df_-al', 'r') as mfile:
                for line in mfile:
                    line = line.split()
                    if line[5] == mount:
                        percUsed = line[4].strip('%')
                        try:
                            percAvail = 100 - int(percUsed)
                        except:
                            percAvail = '-'
                        return {'size': int(line[1]), 'used': line[2], 'avail': line[3], 'percAvail': percAvail, 'percUsed': percUsed}

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
        print colors.WHITE + '\t {:^30}\t {:^20}\t {:^7}    {:^7}    {:^12}'.format('Device', 'Mount Point', 'Size', 'Used', 'Available') + colors.ENDC
        print colors.WHITE + '\t ' + '=' * 30 +'\t ' + '=' * 19 + '\t' + '=' * 8 + '   ' + '=' * 8 + '   ' + '=' * 14 + colors.ENDC
        for mount in mounts:
            try:
                mounts[mount]['size'] = float(mounts[mount]['size']) / 1048576
                mounts[mount]['used'] = float(mounts[mount]['used']) / 1048576
                mounts[mount]['avail'] = float(mounts[mount]['avail']) / 1048576
            except:
                pass
            try:
                print '\t {:<30}\t  {:<12}{:<6}    {:>5.2f} GB   {:>5.2f} GB   {:>5.2f} GB ({:^2}%)'.format(mounts[mount]['dev'], mounts[mount]['mountPoint']\
                    ,mounts[mount]['fsType'], mounts[mount]['size'], mounts[mount]['used'], mounts[mount]['avail'], mounts[mount]['percAvail'])
            except ValueError:
                print '\t {:^30}\t  {:<15} {:<6}'.format(mounts[mount]['dev'], mounts[mount]['mountPoint'], mounts[mount]['fsType'])
                
            if self.showFsOpts:
                print "\t\t " + u"\u2192" + textwrap.fill(mounts[mount]['mountOpts'], 90, subsequent_indent='\t\t  ')

if __name__ == '__main__':
    target = sys.argv[1]
    test = filesys(target)
    test.displayFsInfo()
