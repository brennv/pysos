import sys, os, re
from collections import OrderedDict



def fileToString(filepath):
    try:
        with open(filepath, 'r') as f:
            return f.readline().strip('\n')
    except IOError:
        return '%s not found' %filepath


def getCmdLine(target):
    return fileToString(target + 'proc/cmdline')

def getRelease(target):
        return fileToString(target+'etc/redhat-release')

def getKernelVersion(target):
    uname = fileToString(target + 'sos_commands/kernel/uname_-a')
    return uname.split()[2]


def getRpm(target, rpm, boolean=False):
    rpms = []
    if os.path.isfile(target+'installed-rpms'):
        with open(target+'installed-rpms', 'r') as rfile:
            for line in rfile:
                if line.startswith(rpm):
                    index = line.find('.')
                    thisRpm = line[0:index-2]
                    if thisRpm == rpm:
                        if boolean:
                            return True
                        else:
                            rpms.append(line.split()[0])
    if len(rpms) == 0:
        if boolean:
            return False
        else:
            rpms.append("Not Installed")
    return rpms


def getRpmVer(target, rpm):
    ver = getRpm(target, rpm)
    formatVer = ver[0].strip(rpm).strip('x86_64').strip('noarch').strip('-').strip('.')
    return formatVer

def checkRpm(target, rpm):
    return "Not yet implemented"


def getSysctl(target, sysctl):
    sysctls = {}
    if os.path.isfile(target +'sos_commands/kernel/sysctl_-a'):
        with open(target + 'sos_commands/kernel/sysctl_-a', 'r') as sysfile:
            for line in sysfile:
                if sysctl in line:
                    name = line.split()[0]
                    value = line.split()[2]
                    sysctls[name] = value
    else:
        sysctls = "No sysctl_-a file to parse"
    return sysctls


def getChkConfig(target, service):
    if os.path.isfile(target+'chkconfig'):
        with open(target + 'chkconfig', 'r') as cfile:
            for line in cfile:
                if service in line:
                    serviceStatus = line.lstrip(service).rstrip('\n').lstrip()
                    return serviceStatus
        return "Service not found in chkconfig"
    else:
        return "No chkconfig file found"

def getSeLinux(target):
    selStatus = {}
    if os.path.isfile(target+'sos_commands/selinux/sestatus_-b'):
        with open(target+'sos_commands/selinux/sestatus_-b', 'r') as sfile:
            for i, line in enumerate(sfile):
                index = line.find(':')
                if line.startswith('SELinux status'):
                    selStatus['status'] = line[index+1:len(line)].strip()
                    if selStatus['status'] == 'disabled':
                        selStatus['current'] = 'disabled'
                        selStatus['config'] = 'disabled'
                        break
                elif line.startswith('Current'):
                    selStatus['current'] = line[index+1:len(line)].strip()
                elif line.startswith('Mode'):
                    selStatus['config'] = line[index+1:len(line)].strip()
                elif i > 6:
                    break
    else:
        selStatus['current'] = 'Not Found'
        selStatus['config'] = 'Not Found'
    return selStatus

def getTaintCodes(target):
    # check for kernel taint, well known values go in this dictionary
    t=OrderedDict()
    t['536870912']="Technology Preview code is loaded"
    t['268435456']="Hardware is unsupported"
    t['134217728']="Taint by Zombie"
    t['4096']="Out-of-tree module has been loaded"
    t['2048']="Working around severe firmware bug"
    t['1024']="Modules from drivers/staging are loaded"
    t['512']="Kernel warning occurred"
    t['256']="ACPI table overridden"
    t['128']="Kernel has oopsed before"
    t['64']="User requested taint (software modifying hardware?)"
    t['32']="System has hit bad_page"
    t['16']="System experienced a machine check exception"
    t['8']="User forced a module unload"
    t['4']="SMP with CPUs not designed for SMP"
    t['2']="Module has been forcibly loaded"
    t['1']="Proprietary module has been loaded"
    t['0']="Not tainted. Hooray!"
    

    with open(target + 'proc/sys/kernel/tainted', 'r') as tfile:
        check = tfile.read().splitlines()
        check = check[0]
        #if check in t:
        #    return t[check]
        #else:
        check = int(check)
        taintCodes = []
        for key in t:
            if int(check) - int(key) > int('-1'):
                taintCodes.append(('%4s - '%(key) + t[key]).strip('\n'))
                check = int(check) - int(key)
                if check == 0:
                    return taintCodes
            else:
                pass
        # we should only hit this if we have an undefined taint code remainder from the above
        taintCodes.append("Undefined taint code: %s") %str(check)
        return taintCodes


def parseOutputSection(fname, section):
    with open(fname, 'r') as pfile:
        handle_regex = re.compile('^%s\s'%section)
        newline = re.compile('^$')
        lines = pfile.readlines()
        for x in range(0,len(lines)):
            line = lines[x]
            if handle_regex.findall(line):
            # Found header for section
                sectionInfo = {}
                sectionInfo['info'] = [] 
                while True:
                    try:
                        line = lines[x+1]
                # repeat until we hit newline
                        if not newline.findall(line):
                             sectionInfo['info'].append(line.strip().strip('\t'))
                             x += 1
                        else:
                            break
                    except:
                        break

                info = {}
                for item in sectionInfo['info']:
                    try:
                        key = item.split(':')[0]
                        value = item.split(':')[1]
                        info[key] = value
                    except:
                        pass
    return info
    
