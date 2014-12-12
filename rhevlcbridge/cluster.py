'''
Created on Dec 27, 2013

@author: wallace
'''

class Cluster():
    '''
    This class will represent hosts in an environment
    '''

    uuid = ""
    name = ""
    cpu_type = ""
    dc_uuid = ""
    compat_ver = ""

    schema31 = {
        "uuid": 0,
        "name": 1,
        "cpu_type": 3,
        "dc_uuid": 11,
        "compat_ver": 13,
    }
    schema32 = {
        "uuid": 0,
        "name": 1,
        "cpu_type": 3,
        "dc_uuid": 11,
        "compat_ver": 12,
    }
    schema33 = {
        "uuid": 0,
        "name": 1,
        "cpu_type": 3,
        "dc_uuid": 6,
        "compat_ver": 8,
    }
    schema34 = {
        "uuid": 0,
        "name": 1,
        "cpu_type": 3,
        "dc_uuid": 6,
        "compat_ver": 8,
    }

    def __init__(self, csvList, dbVersion):
        '''
        This constructor assumes it is being passed a comma separated list consisting of all elements in a line from the dat file
        '''
        details = csvList

        current_schema = "3.3"   # arbitrary, just to set a default
        if dbVersion == "3.1":
            current_schema = self.schema31
        elif dbVersion == "3.2":
            current_schema = self.schema32
        elif dbVersion == "3.3":
            current_schema = self.schema33
        elif dbVersion == "3.4":
            current_schema = self.schema34

        if len(details) > 2:
            self.uuid = details[current_schema['uuid']]
            self.name = details[current_schema['name']]
            self.cpu_type = details[current_schema['cpu_type']]
            self.dc_uuid = details[current_schema['dc_uuid']]
            if len(self.dc_uuid) != 36:
                self.dc_uuid = details[6] # 3.3 and 3.4 moved this column to the 6th position instead of 11
            self.compat_ver = details[current_schema['compat_ver']]
            #print self.dc_uuid
            #print len(self.dc_uuid)
            if len(self.dc_uuid) != 36:
                self.dc_uuid = details[10]
            #print "We made a cluster!"


    def get_dc_uuid(self):
        return self.dc_uuid


    def set_dc_uuid(self, value):
        self.dc_uuid = value

    def get_compat_ver(self):
        return self.compat_ver

    def set_compat_ver(self, value):
        self.compat_ver = value

    def del_dc_uuid(self):
        del self.dc_uuid


    def get_uuid(self):
        return self.uuid


    def get_name(self):
        return self.name


    def get_cpu_type(self):
        return self.cpu_type


    def set_uuid(self, value):
        self.uuid = value


    def set_name(self, value):
        self.name = value


    def set_cpu_type(self, value):
        self.cpu_type = value


    def del_uuid(self):
        del self.uuid


    def del_name(self):
        del self.name


    def del_cpu_type(self):
        del self.cpu_type

    uuid = property(get_uuid, set_uuid, del_uuid, "uuid's docstring")
    name = property(get_name, set_name, del_name, "name's docstring")
    cpu_type = property(get_cpu_type, set_cpu_type, del_cpu_type, "cpu_type's docstring")
    dc_uuid = property(get_dc_uuid, set_dc_uuid, del_dc_uuid, "dc_uuid's docstring")




