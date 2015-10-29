import json
import os
import sys
from . import pysosutils
from .colors import Color as c


class Object:
    pass


class docker:

    ''' Obtain docker and container related information '''

    def __init__(self, target):
        self.target = target
        self.pprint = c()

    def _fmtNodeName(self, node):
        return node.split('=')[2].strip('http://')[0:-2]

    def _parseJson(self, f):
        return json.loads("".join(open(f).readlines()))

    def checkIsAtomic(self):
        if not os.path.exists("/host/etc/system-release-cpe"):
            return False
        cpe = open("/host/etc/system-release-cpe", "r").readlines()
        return ':atomic-host' in cpe[0]

    def getAtomicInfo(self):
        ainfo = Object()
        if self.checkIsAtomic():
            return "Atomic Host - branch WIP"
        else:
            return False

    def getImageList(self):
        try:
            images = []
            with open(self.target +
                      'sos_commands/docker/docker_images') as d:
                for line in d:
                    l = line.split()
                    i = Object()
                    i.repo = l[0]
                    i.tag = l[1]
                    i.image = l[2]
                    i.size = l[4]
                    images.append(i)
            return images
        except IOError:
            return False

    def getDockerInfo(self):
        try:
            with open('sos_commands/docker/docker_info') as dfile:
                info = {}
                for line in dfile:
                    line = line.split(':')
                    info[line[0]] = line[1].strip()
            dinfo = Object()
            for key in info:
                setattr(dinfo, key.replace(" ", '').lower(), info[key])
            dinfo.dockerversion = pysosutils.getRpmVer(self.target, 'docker')
            with open('sos_commands/docker/docker_images') as ifile:
                images = []
                for line in ifile:
                    line = line.split()
                    if line[2] in images:
                        pass
                    else:
                        images.append(line[2])
                dinfo.uniqueimages = images
            with open('sos_commands/docker/docker_ps') as pfile:
                containers = []
                for line in pfile:
                    if not line.startswith('CONTAINER'):
                        line = line.split()
                        container = Object()
                        container.id = line[0]
                        container.image = line[1]
                        container.cmd = line[2]
                        container.status = line[4]
                        container.name = line[6]
                        containers.append(container)
                dinfo.containers = containers
            return dinfo
        except:
            return False

    def getKubeInfo(self):
        kinfo = Object()
        kinfo.version = pysosutils.getRpmVer(self.target, 'kubernetes')
        if "Not Installed" not in kinfo.version:
            try:
                kinfo.minions = self._parseJson(
                    'sos_commands/kubernetes/kubectl_get_-o_json_minions'
                )
                kinfo.node = "Master"
            except ValueError:
                kinfo.minions = False
                # 'node' not 'minion' now since that translates poorly
                kinfo.node = "Node"
                kinfo.master = ''
            except Exception as e:
                kinfo.minions = False
                kinfo.node = "Unknown"
                print("Unhandled exception, please report this")
                print(e)
            try:
                kinfo.pods = self._parseJson(
                    'sos_commands/kubernetes/kubectl_get_-o_json_pods'
                )
            except ValueError:
                kinfo.pods = False
            try:
                kinfo.services = self._parseJson(
                    'sos_commands/kubernetes/kubectl_get_-o_json_services'
                )
            except:
                kinfo.services = False
            try:
                kinfo.rc = self._parseJson(
                    'sos_commands/kubernetes/kubectl_get_-o_json_replicationController'
                )
            except:
                kinfo.rc = False
            if kinfo.node == "Node":
                with open('etc/kubernetes/config') as kfile:
                    for line in kfile:
                        if 'KUBE_ETCD_SERVERS' in line:
                            kinfo.etcd = self._fmtNodeName(line)
                        elif 'KUBE_MASTER' in line:
                            kinfo.master = self._fmtNodeName(line)
            return kinfo
        else:
            kinfo.installed = False
            return kinfo

    def displayContainerInfo(self):
        self.dinfo = self.getDockerInfo()
        self.kinfo = self.getKubeInfo()
        self.ainfo = self.getAtomicInfo()

        self.pprint.bsection('Containerization')

        self.displayDockerInfo()
        self.displayAtomicInfo()
        self.displayKubeInfo()

    def displayAtomicInfo(self):
        if self.ainfo:
            self.pprint.bheader('\tAtomic Information : ', self.ainfo.info)

    def displayDockerInfo(self):
        if self.dinfo:
            self.pprint.bheader('\n\tDocker Version     : ',
                                self.dinfo.dockerversion
                                )
            self.pprint.bheader('\tKubernetes Version : ', self.kinfo.version)
            self.pprint.bheader('\tUnique Images      : ',
                                str(len(self.dinfo.uniqueimages))
                                )
            self.pprint.bheader('\tRunning Containers : ',
                                str(len(self.dinfo.containers))
                                )
            print('')
            for container in self.dinfo.containers:
                print('\t\t {id:15} {image:25} {cmd}'.format(
                    id=container.id,
                    image=container.image,
                    cmd=container.cmd
                ))
        else:
            self.pprint.red(
                "\t Docker info could not be parsed. Was sos run with docker plugin?"
            )

    def displayKubeInfo(self):
        if self.kinfo.installed:
            self.pprint.bheader('\n\t{0:22} : '.format(
                                'Kubernetes Role'
                                ),
                                kinfo.node
                                )
            if kinfo.node == "Node":
                self.pprint.cyan('\t\t Master Node   : ', kinfo.master)
            if kinfo.minions:
                self.pprint.cyan('\t\t Kubelet Nodes : ')
                for minion in kinfo.minions['items']:
                    print('\t\t\t\t{node:20} {st:<10}'.format(
                        node=minion['spec']['externalID'],
                        st=minion['status']['conditions'][0]['type']
                    ))
    
            if kinfo.pods:
                self.pprint.white('\t\t Active Pods   : ')
                self.pprint.white('\t\t\t\t{pod:^15} {host:^12} {st:^12}'.format(
                    pod='Pod Name',
                    host='Node',
                    st='Status'
                )
                )
                for pod in kinfo.pods['items']:
                    print('\t\t\t\t{pod:15} {node:15} {status:15}'.format(
                        pod=pod['metadata']['name'][:15],
                        node=pod['spec']['host'],
                        status=pod['status']['phase']
                    ))
    
            if kinfo.services:
                self.pprint.red('\t\t Services      : ')
                self.pprint.red('\t\t\t\t{n:^15} {t:5} {p:^5} {c} {i:>11}'.format(
                    n='Service Name',
                    t='Type',
                    p='Port',
                    c='C.Port',
                    i='Portal IP'
                )
                )
                for serv in kinfo.services['items']:
                    print('\t\t\t\t{n:15} {t:5} {p:<5} {c:5}   {i}'.format(
                        n=serv['metadata']['name'][:15],
                        t=serv['spec']['ports'][0]['protocol'],
                        p=serv['spec']['ports'][0]['port'],
                        c=serv['spec']['ports'][0]['targetPort'],
                        i=serv['spec']['portalIP']
                    ))
            if kinfo.rc:
                self.pprint.blue('\t\t Controllers   : ')
                self.pprint.blue('\t\t\t\t{n:^15} {c:10} {i:10} {s:10} {r:5}'.format(
                    n="Controller",
                    c="Container",
                    i="Image",
                    s="Selector",
                    r="Replicas"
                )
                )
                for rc in kinfo.rc['items']:
                    print('\t\t\t\t{n:^15} {c:10} {i:10} {s:^10} {r:5}'.format(
                        n=rc['metadata']['name'][:15],
                        c=rc['spec']['template']['spec'][
                            'containers'][0]['name'][:10],
                        i=rc['spec']['template']['spec'][
                            'containers'][0]['image'][:10],
                        s=rc['spec']['selector']['name'],
                        r=rc['status']['replicas']
                    ))

if __name__ == '__main__':
    target = sys.argv[1]
    test = docker(target)
    test.getDockerInfo()
