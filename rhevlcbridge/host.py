'''
Created on Dec 27, 2013

@author: wallace
'''

class Host():
    '''
    This class will represent hosts in an environment
    '''

    # CHANGED: In this branch I'm moving from the vds_static table to the vds view - a single view with information from both statuc and dynamic tables
    uuid = ""
    name = ""
    host_dc_uuid = ""
    host_dc_name = "unknown"
    ip_addr = ""
    host_name = ""
    host_type = ""
    spm_status = ""
    releaseVer = "unknown"
    vdsm_ver = ""
    host_os = ""
    kvm_ver = ""
    spice_ver = ""
    kernel_ver = ""
    selinux = "Unknown"   # Setting to unknown by default since the variable is set in the rhevm.py file. if the file can't be found or opened, unknown is returned
    current_scheme = ""

    schema31 = {
        "uuid": 0,
        "name": 1,
        "host_dc_uuid": 6,
        "ip_addr": 2,
        "host_name": 4,
        "host_type": 8,
        "vdsm_ver": 39,
        "host_os": 27,
        "kvm_ver": 28,
        "spice_ver": 29,
        "kernel_ver": 30
    }
    schema32 = {
        "uuid": 0,
        "name": 1,
        "host_dc_uuid": 6,
        "ip_addr": 2,
        "host_name": 4,
        "host_type": 8,
        "vdsm_ver": 37,
        "host_os": 25,
        "kvm_ver": 26,
        "spice_ver": 27,
        "kernel_ver": 28
    }
    schema33 = {
        "uuid": 0,
        "name": 1,
        "host_dc_uuid": 6,
        "ip_addr": 2,
        "host_name": 4,
        "host_type": 8,
        "vdsm_ver": 38,
        "host_os": 26,
        "kvm_ver": 27,
        "spice_ver": 28,
        "kernel_ver": 29
    }
    schema34 = {
        "uuid": 0,
        "name": 1,
        "host_dc_uuid": 6,
        "ip_addr": 2,
        "host_name": 4,
        "host_type": 8,
        "vdsm_ver": 36,
        "host_os": 25,
        "kvm_ver": 26,
        "spice_ver": 27,
        "kernel_ver": 28
    }
    schema35 = {
        "uuid": 0,
        "name": 1,
        "host_dc_uuid": 6,
        "ip_addr": 2,
        "host_name": 4,
        "host_type": 8,
        "vdsm_ver": 35,
        "host_os": 24,
        "kvm_ver": 25,
        "spice_ver": 26,
        "kernel_ver": 27
    }

    def __init__(self, csvList, dbVersion):
        """
        This constructor assumes it is being passed a comma separated list consisting of all elements in a line from the dat file
        """
        details = csvList

        if len(details) > 2:
            self.current_schema = "3.3"   # arbitrary, just to set a default
            if dbVersion == "3.1":
                self.current_schema = self.schema31
            elif dbVersion == "3.2":
                self.current_schema = self.schema32
            elif dbVersion == "3.3":
                self.current_schema = self.schema33
            elif dbVersion == "3.4":
                self.current_schema = self.schema34
            elif dbVersion == "3.5":
                self.current_schema = self.schema35

            self.uuid = details[self.current_schema['uuid']]
            self.name = details[self.current_schema['name']]
            self.host_dc_uuid = details[self.current_schema['host_dc_uuid']]
            self.ip_addr = details[self.current_schema['ip_addr']]
            self.host_name = details[self.current_schema['host_name']]
            self.type = details[self.current_schema['host_type']]
            # determine host type from input
            if self.type == "0":
                self.set_type("RHEL")
            elif self.type == "2":
                self.set_type("RHEV-H")
            self.host_dc_name = 'unknown'

    def get_spm_status(self):
        return self.spm_status


    def set_spm_status(self, value):
        self.spm_status = value


    def get_host_dc_name(self):
        return self.host_dc_name


    def set_host_dc_name(self, value):
        self.host_dc_name = value


    def del_host_dc_name(self):
        del self.host_dc_name

    def get_spm(self):
        return self.spm_status


    def get_release_ver(self):
        return self.releaseVer

    def set_spm(self, value):
        self.spm_status = value


    def set_release_ver(self, value):
        self.releaseVer = value


    def del_spm(self):
        del self.spm_status


    def del_release_ver(self):
        del self.releaseVer


    def get_selinux(self):
        return self.selinux

    def set_selinux(self, status):
        self.selinux = status

    def isSPM(self, spm_uuid):
        if spm_uuid == self.get_uuid():
            return True
        else:
            return False

    def get_type(self):
        return self.host_type

    def set_type(self, value):
        self.host_type = value

    def del_type(self):
        del self.host_type

    def get_uuid(self):
        return self.uuid

    def get_name(self):
        return self.name

    def get_host_dc_uuid(self):
        return self.host_dc_uuid

    def get_ip_addr(self):
        return self.ip_addr

    def get_host_name(self):
        return self.host_name

    def set_uuid(self, value):
        self.uuid = value

    def set_name(self, value):
        self.name = value

    def set_host_dc_uuid(self, value):
        self.host_dc_uuid = value

    def set_ip_addr(self, value):
        self.ip_addr = value

    def set_host_name(self, value):
        self.host_name = value

    def del_uuid(self):
        del self.uuid

    def del_name(self):
        del self.name

    def del_host_dc_uuid(self):
        del self.host_dc_uuid

    def del_ip_addr(self):
        del self.ip_addr

    def del_host_name(self):
        del self.host_name

    def get_vdsm_ver(self):
        return self.vdsm_ver

    def get_host_os(self):
        return self.host_os

    def get_kvm_ver(self):
        return self.kvm_ver

    def get_spice_ver(self):
        return self.spice_ver

    def get_kernel_ver(self):
        return self.kernel_ver

    def __repr__(self):
        print "Host name: " + self.name
        print "VDSM Ver: " + self.vdsm_ver

    def updateHostDynamic(self, dynamic_list):

        self.vdsm_ver = dynamic_list[self.current_schema['vdsm_ver']]
        if 'vdsm' not in self.vdsm_ver:
             self.vdsm_ver = "error"
        else:
             self.vdsm_ver = self.vdsm_ver.split("vdsm-")[1].rstrip('\n')
        self.host_os = dynamic_list[self.current_schema['host_os']].replace(' ','')
        self.kvm_ver = dynamic_list[self.current_schema['kvm_ver']].replace(' ','')
        self.spice_ver = dynamic_list[self.current_schema['spice_ver']].replace(' ','')
        self.kernel_ver = dynamic_list[self.current_schema['kernel_ver']].replace(' ','')

    host_dc_name = property(get_host_dc_name, set_host_dc_name, del_host_dc_name, "host_dc_name's docstring")
    _spm_status = property(get_spm_status, set_spm_status, None, None)



