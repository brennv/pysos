from .colors import Color as c


class VolumeGroup:

    def __init__(self, rawdata):
        self.rawdata = rawdata
        self.name = None
        self.access = None
        self.status = None
        self.size = None
        self.status = None
        vglvdata, pvdata = [x.split(
            '+++') for x in '+++'.join(self.rawdata).split(
                                            '--- Physical volumes ---')]
        self.getvgdata(vglvdata)
        self.lvs = self.getlvs(vglvdata)
        self.pvs = self.getpvs(pvdata)
        self.pprint = c()

    def getvgdata(self, vglvdata):
        self.vgdata = [
            x for x in '+++'.join(vglvdata).split(
                            '--- Logical volume ---')[0].split('+++') if x]
        for l in self.vgdata:
            if 'VG Name' in l:
                self.name = l.split()[-1]
            elif 'VG Access' in l:
                self.access = l.split()[-1]
            elif 'VG Status' in l:
                self.status = l.split()[-1]
            elif 'VG Size' in l:
                self.size = ' '.join(l.split()[-2:])
            elif 'VG UUID' in l:
                self.uuid = l.split()[-1]

    def getlvs(self, vglvdata):
        self.lvdata = [x.split(
            '+++') for x in '+++'.join(vglvdata).split(
                                        '--- Logical volume ---')[1:] if x]
        lvs = []
        for i in self.lvdata:
            lv = {}
            for l in i:
                if 'LV' in l:
                    if 'Size' in l:
                        lv['size'] = " ".join(l.split()[-2:])
                    elif 'Creation' not in l:
                        attr = l.split()[-2].lower()
                        lv[attr] = l.split()[-1]
            lvs.append(LogicalVolume(lv))
        return lvs

    def getpvs(self, pvdata):
        self.pvdata = [x for x in pvdata if x]
        pvsdict = {}
        for l in self.pvdata:
            if 'PV Name' in l:
                name = l.split()[-1]
                if name not in list(pvsdict.keys()):
                    pvsdict[name] = {}
                    pvsdict[name]['name'] = name
            elif name:
                attr = l.split()[-2].lower()
                pvsdict[name][attr] = l.split()[-1]
        pvs = []
        for pv in list(pvsdict.values()):
            pvs.append(PhysicalVolume(pv))
        return pvs


class LogicalVolume:

    def __init__(self, lvdict):
        for k, v in lvdict.items():
            self.__dict__[k] = v


class PhysicalVolume:

    def __init__(self, pvdict):
        for k, v in pvdict.items():
            self.__dict__[k] = v


class lvm:

    def __init__(self, target):
        self.target = target + 'sos_commands/devicemapper/vgdisplay_-vv'
        self.pprint = c()

    def getLvmInfo(self):
        try:
            data = [l.strip() for l in open(self.target).readlines()
                    if l.strip() and (l.strip().startswith('---') or
                                      l.strip().startswith('VG') or
                                      l.strip().startswith('LV') or
                                      l.strip().startswith('PV'))]
            vgs = []
            for x in [i for i in '+++'.join(data).split(
                    '--- Volume group ---') if i]:
                vg = VolumeGroup(x.split('+++'))
                vgs.append(vg)
        except IOError:
            vgs = False
            self.pprint.bred(
                '\tCould not find %s. Unable to parse' % self.target
            )
        return vgs

    def displayVgInfo(self):
        self.pprint.bsection('Disk and LVM Information')
        print('')
        vgs = self.getLvmInfo()
        if vgs:
            if len(vgs) > 0:
                for vg in vgs:
                    self.pprint.bheader('\t VG Name:  ', vg.name)
                    print('')
                    self.pprint.white(
                        '\t\t {:^15} {:^12}'.format(
                            'LV NAME',
                            'SIZE'
                        )
                    )
                    for lv in vg.lvs:
                        print('\t\t  {:^15} {:>12}'.format(lv.name, lv.size))
                    print('')
                    print('\t\t  PVs in this VG: ' + ' '.join(
                        pv.name for pv in vg.pvs))

if __name__ == '__main__':
    for vg in vgs:
        print("VG %s:" % vg.name)
        for lv in vg.lvs:
            print("\tLV %s (%s)" % (lv.name, lv.size))
        for pv in vg.pvs:
            print("\tPV %s" % pv.name)
