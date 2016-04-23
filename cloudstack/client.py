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
        for vm in ret.get('virtualmachine'):
            vms.append({'id': vm['id'], 'nic': vm['nic']})

        return vms

class Client(object):
    def __init__(self, url, apikey, secretkey):
        self.conn = CloudStackAdminDriver(url=url, key=apikey, secret=secretkey)

    def get_vlaniprange(self, uuid):
        ranges = self.conn.list_vlanipranges()
        return ranges[uuid]

    def get_vms(self, podid):
        return self.conn.list_vms(podid)