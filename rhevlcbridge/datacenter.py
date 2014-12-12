'''
Created on Dec 27, 2013

@author: wallace
'''

class DataCenter():
    '''
    This class will represent hosts in an environment
    '''

    uuid = ""
    name = ""
    compat = ""
    spm_uuid = ""

    # since each db version changes a little bit, we need to define the index of each field in the dat file
    schema31 = {
        "uuid": 0,
        "name": 1,
        "compat": 8,
        "spm_uuid": 7
    }
    schema32 = {
        "uuid": 0,
        "name": 1,
        "compat": 8,
        "spm_uuid": 7
    }
    schema33 = {
        "uuid": 0,
        "name": 1,
        "compat": 8,
        "spm_uuid": 7
    }
    schema34 = {
        "uuid": 0,
        "name": 1,
        "compat": 8,
        "spm_uuid": 7
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
            self.compat = details[current_schema['compat']]
            self.spm_uuid = details[current_schema['spm_uuid']]

    def get_uuid(self):
        return self.uuid


    def get_name(self):
        return self.name


    def get_compat(self):
        return self.compat


    def get_spm_uuid(self):
        return self.spm_uuid


    def set_uuid(self, value):
        self.uuid = value


    def set_name(self, value):
        self.name = value


    def set_compat(self, value):
        self.compat = value


    def set_spm_uuid(self, value):
        self.spm_uuid = value


    def del_uuid(self):
        del self.uuid


    def del_name(self):
        del self.name


    def del_compat(self):
        del self.compat


    def del_spm_uuid(self):
        del self.spm_uuid

    uuid = property(get_uuid, set_uuid, del_uuid, "uuid's docstring")
    name = property(get_name, set_name, del_name, "name's docstring")
    compat = property(get_compat, set_compat, del_compat, "compat's docstring")
    spm_uuid = property(get_spm_uuid, set_spm_uuid, del_spm_uuid, "spm_uuid's docstring")


