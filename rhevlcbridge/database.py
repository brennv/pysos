'''
Created on Dec 27, 2013

@author: wallace
'''
import tarfile, os
from host import Host  # Surely there is a better way to do this
from storagedomain import StorageDomain
from datacenter import DataCenter
from cluster import Cluster
from task import Task


class Database():
    '''
    This class should be created by passing the sos_pgdump.tar file to it

    It will serve the purpose of pulling information from the tar file without the need to upload to a dbviewer
    '''

    ''' Start declaring variables for the class'''
    dbDir = ""
    tarFile = ""
    dat_files = []  # this is a list for all the wanted dat files
    data_centers = []
    storage_domains = []
    hosts = []
    clusters = []
    tasks = []
    dbVersion = ""

    def __init__(self, dbFile, dbVersion):
        '''
        Constructor
        '''
        self.dbVersion = dbVersion
        self.dbDir = os.path.dirname(dbFile) + "/"
        tarFile = tarfile.open(dbFile)
        self.unpack(tarFile, self.dbDir)

        # Now that we're unpacked, move on to gathering information
        self.data_centers = self.gatherDataCenters(dbVersion)
        self.storage_domains = self.gatherStorageDomains(dbVersion)
        self.hosts = self.gatherHosts(dbVersion)
        self.clusters = self.gatherClusters(dbVersion)
        self.tasks = self.gatherTasks(dbVersion)


    def get_clusters(self):
        return self.clusters


    def set_clusters(self, value):
        self.clusters = value


    def del_clusters(self):
        del self.clusters


    def get_data_centers(self):
        return self.data_centers


    def get_storage_domains(self):
        return self.storage_domains

    def get_hosts(self):
        return self.hosts

    def get_tasks(self):
        return self.tasks


    def unpack(self, tarFile, dbDir):
        # Start with extraction
        tarFile.extractall(dbDir)

        # create list of dat files
        self.dat_files = ["data_center_dat",
                          "storage_domain_dat",
                          "host_dat",
                          "cluster_dat",
                          "async_tasks_dat",
                          "host_dynamic_dat"]

        self.dat_files[0] = self.dat_files[0] + "," + self.findDat(" storage_pool ", dbDir + "restore.sql")
        self.dat_files[1] = self.dat_files[1] + "," + self.findDat(" storage_domain_static ", dbDir + "restore.sql")
        self.dat_files[2] = self.dat_files[2] + "," + self.findDat(" vds_static ", dbDir + "restore.sql")
        self.dat_files[3] = self.dat_files[3] + "," + self.findDat(" vds_groups ", dbDir + "restore.sql")
        self.dat_files[4] = self.dat_files[4] + "," + self.findDat(" async_tasks ", dbDir + "restore.sql")
        self.dat_files[5] = self.dat_files[5] + "," + self.findDat(" vds_dynamic ", dbDir + "restore.sql")

    # print self.dat_files[3]

    def findDat(self, table, restFile):
        '''
        Subroutine to find the .dat file name in restore.sql
        '''
        openFile = open(restFile, "r")
        lines = openFile.readlines()

        for n in lines:
            if n.find(table) != -1:
                if n.find("dat") != -1:
                    datInd = n.find("PATH")
                    datFileName = n[datInd + 7:datInd + 15]
                    if datFileName.endswith("dat"):
                        #print "Found dat line for " + table
                        #logging.warning('Return dat file: ' +datFileName)
                        return datFileName


    def gatherDataCenters(self, dbVersion):
        '''
        This method returns a list of comma-separated details of the Data Center
        '''
        dc_list = []
        #print self.dbDir
        #print self.dat_files[0]
        dat_file = self.dbDir + self.dat_files[0].split(",")[1]
        openDat = open(dat_file, "r")

        lines = openDat.readlines()

        for l in lines:
            if len(l.split("\t")) > 1:
                newDC = DataCenter(l.split("\t"), dbVersion)
                dc_list.append(newDC)

        openDat.close()
        return dc_list

    def gatherStorageDomains(self, dbVersion):
        '''
        This method returns a list of comma-separated details of the Storage Domains
        '''
        sd_list = []
        dat_file = self.dbDir + self.dat_files[1].split(",")[1]
        #print dat_file
        openDat = open(dat_file, "r")

        lines = openDat.readlines()

        for l in lines:
            if len(l.split("\t")) > 1:
                #print "Line: " + l
                newSD = StorageDomain(l.split("\t"), dbVersion)
                sd_list.append(newSD)

        openDat.close()
        return sd_list

    def gatherClusters(self, dbVersion):
        '''
        This method returns a list of comma separated details for clusters
        '''
        cl_list = []
        dat_file = self.dbDir + self.dat_files[3].split(",")[1]

        openDat = open(dat_file, "r")

        lines = openDat.readlines()
        #print len(lines)

        for l in lines:
            if len(l.split("\t")) > 1:
                newCluster = Cluster(l.split("\t"), dbVersion)
                #print "New Cluster: " + newCluster.get_dc_uuid()
                #print "Cluster Name: " + newCluster.get_name()
                cl_list.append(newCluster)

        openDat.close()
        return cl_list

    def gatherHosts(self, dbVersion):
        """
        This method returns a list of comma-separated details of the Data Center
        """
        host_list = []
        static_dat_file = self.dbDir + self.dat_files[2].split(",")[1]
        dynamic_dat_file = self.dbDir + self.dat_files[5].split(",")[1]
        #print dat_file
        open_static = open(static_dat_file, "r")
        open_dynamic = open(dynamic_dat_file, "r")

        lines = open_static.readlines()

        for l in lines:
            if len(l.split("\t")) > 1:
                #print l.split("\t")
                newHost = Host(l.split("\t"), dbVersion)
                #print "New Host Name: " + newHost.get_name()
                host_list.append(newHost)

        # fill in vds_dynamic information
        lines = open_dynamic.readlines()
        for host in host_list:
            h_uuid = host.get_uuid()
            for l in lines: # cycle through all lines in vds_dynamic file
                if h_uuid in l: # if this line correlates to the current host
                    host.updateHostDynamic(l.split("\t")) # send line to Host method as a list

        open_static.close()
        open_dynamic.close()
        return host_list

    def gatherTasks(self, dbVersion):

        task_list = []
        dat_file = self.dbDir + self.dat_files[4].split(",")[1]

        openDat = open(dat_file, "r")

        lines = openDat.readlines()

        for l in lines:
            if len(l.split("\t")) > 1:
                newTask = Task(l.split("\t"), dbVersion)
                task_list.append(newTask)

        openDat.close()
        return task_list


    data_centers = property(get_data_centers, None, None, None)
    storage_domains = property(get_storage_domains, None, None, None)
    hosts = property(get_hosts, None, None, None)
    clusters = property(get_clusters, set_clusters, del_clusters, "clusters's docstring")

