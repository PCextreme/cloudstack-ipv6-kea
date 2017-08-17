from libcloud.compute.drivers.cloudstack import CloudStackNodeDriver


class CloudStackAdminDriver(CloudStackNodeDriver):
    def __init__(self, url, key, secret):
        super(CloudStackAdminDriver, self).__init__(key=key,
                                                    secret=secret,
                                                    url=url,
                                                    secure=True)

    def list_vlanipranges(self, podid=None):
        args = {}
        if podid is not None:
            args['podid'] = podid

        ranges = {}
        ret = self._sync_request(command='listVlanIpRanges', method='GET',
                                 params=args)
        for range in ret.get('vlaniprange'):
            try:
                ranges[range['id']] = {'podid': range['podid'],
                                       'networkid': range['networkid'],
                                       'gateway': range['gateway'],
                                       'ip6cidr': range['ip6cidr']}
            except KeyError:
                pass

        return ranges

    def list_vms(self, podid):
        vms = []
        ret = self._sync_request(command='listVirtualMachines', method='GET',
                                 params={'podid': podid})
        if not ret:
            return vms

        for vm in ret.get('virtualmachine'):
            vms.append({'id': vm['id'], 'nic': vm['nic']})

        return vms


class Client(object):
    def __init__(self, url, apikey, secretkey):
        self.conn = CloudStackAdminDriver(url=url, key=apikey, secret=secretkey)

    def get_vlanipranges(self):
        return self.conn.list_vlanipranges()

    def get_vlaniprange(self, uuid):
        return self.get_vlanipranges()[uuid]

    def get_vms(self, podid):
        return self.conn.list_vms(podid)

    def get_vlans_vms(self):
        ranges = dict()
        for key, value in self.get_vlanipranges().items():
            value['vms'] = self.get_vms(value['podid'])
            ranges[key] = value

        return ranges
