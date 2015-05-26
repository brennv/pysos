import sys
import os
import textwrap
from collections import OrderedDict
from colors import Color as c

class Object(object):
    pass

class filesys():
    """ Capture and optionally display filesystem data """
    def __init__(self, target, showFsOpts=False):
        self.target = target
        self.pprint = c()
        self.showFsOpts = showFsOpts
        self.excludes = ['cgroup', 'tmpfs', 'none', 'sunrpc', 'debugfs',
            'configfs', 'fusectl', 'hugetlbfs', 'devpts', 'sysfs',
            'mqueue', 'systemd', 'proc', 'devtmpfs', 'securityfs',
            'pstore', 'binfmt_misc']

    def getFsMounts(self):
        """ Get a list of all mounts from sosreport """
        if os.path.isfile(
                self.target + 'sos_commands/filesys/mount_-l'):
            mounts = []
            with open(self.target + 'sos_commands/filesys/mount_-l',
                        'r') as mfile:
                for line in mfile:
                    if line.startswith(tuple(self.excludes)):
                        pass
                    else:
                        mount = Object()
                        line2 = line.strip('\n').split()
                        try:
                            mount.name = line2[0]
                            mount.dev = line2[0].replace("/dev/mapper/",
                            '').replace("/dev/", '')
                            mount.mountpoint = line2[2].strip()
                            mount.fstype = line2[4]
                            mount.mountopts = line[line.find('(')+1:
                                            line.find(')')-2].strip()
                        except:
                            pass
                        mounts.append(mount)
            return mounts
        else:
            return False

    def getFsSize(self, mount):
        """ Get filesystem size data for a given mount """ 
        dev = Object()
        if os.path.isfile(self.target + 'sos_commands/filesys/df_-al'):
            mount = mount.strip()
            with open(self.target + 'sos_commands/filesys/df_-al',
                        'r') as mfile:
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
                            dev.size = int(line[0])
                            dev.used = line[1]
                            dev.avail = int(line[2])
                            dev.percavail = percAvail
                            dev.percused = percUsed
                            return dev
                    except:
                        pass
        dev.size = ''
        dev.used = ''
        dev.avail = ''
        dev.percavail = ''
        dev.percused = ''
        return dev

    def getFsDev(self, mount):
        """ Get the backing device for a given mountpoint """
        if os.path.isfile(self.target + 'sos_commands/filesys/mount_-l'):
            with open(self.target + 'sos_commands/filesys/mount_-l',
                        'r') as mfile:
                for line in mfile:
                    if line.split()[2] == mount:
                        return line.split()[0]
            # if we don't hit anything, return that fact
            return 'Unknown Mount Device'
        else:
            return 'Cannot find mount file'
        

    def getAllMountInfo(self):
        """ Compile all data for all mounts in sosreport """
        mounts = self.getFsMounts()
        for mount in mounts:
            try:
                dev = self.getFsSize(mount.mountpoint)
                mount.__dict__.update(dev.__dict__)
            except AttributeError:
                mounts.remove(mount)
        return mounts

    def displayFsInfo(self):
        """ Display data from getAllMountInfo() """
        mounts = self.getAllMountInfo()
        for mount in mounts:
            if mount.size < 1 or 'tmpfs' in mount.dev:
                del mount
        self.pprint.bsection('File System Information')
        print ''
        self.pprint.white(
                '\t {:^25}\t{:^20}\t  {:^7}    {:^7}\t  {:>11}'.format(
                    'Device', 'Mount Point', 'Size', 'Used','Available'
                    )
                )
        sep = '\t ' + '=' * 25 +'\t ' + '=' * 19 + '\t'\
                + '=' * 9 + '  ' + '=' * 9 + '    ' + '=' * 18
        self.pprint.white(sep)
        for mount in mounts:
            try:
                mount.size = float(mount.size) / 1048576
                mount.used = float(mount.used) / 1048576
                mount.avail = float(mount.avail) / 1048576
            except:
                pass
            try:
                print '\t {:<25}\t {:<15} {:<6} {:>7.2f} GB'.format(
                mount.dev, mount.mountpoint, mount.fstype,
                mount.size) + ' {:>7.2f} GB\t{:>7.2f} GB'.format(
                mount.used, mount.avail) + ' ({:^2}%)'.format(
                mount.percavail)
            except:
                print '\t {:<25}\t {:<15} {:<6}'.format(mount.dev,
                                        mount.mountpoint, mount.fstype)
                
            if self.showFsOpts:
                print "\t\t " + u"\u2192" + textwrap.fill(
                        mount.mountopts, 90, subsequent_indent='\t\t  ')

if __name__ == '__main__':
    target = sys.argv[1]
    test = filesys(target)
    test.displayFsInfo()
