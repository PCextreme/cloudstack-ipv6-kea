from libcloud.compute.drivers.cloudstack import CloudStackNodeDriver


class CloudStackAdminDriver(CloudStackNodeDriver):
    def __init__(self, url, key, secret):
        super(CloudStackAdminDriver, self).__init__(key=key,
                                                    secret=secret,
                                                    url=url,
                                                    secure=True)

    def list_vlanipranges(self):
        ranges = {}
        ret = self._sync_request(command='listVlanIpRanges', method='GET')
        for range in ret.get('vlaniprange'):
            try:
                ranges[range['id']] = {'podid': range['podid'],
                                       'networkid': range['networkid'],
                                       'ip6cidr': range['ip6cidr']}
            except KeyError:
                pass

        return ranges

    def list_vms(self, podid):
        vms = []
        ret = self._sync_request(command='listVlanIpRanges', method='GET')

class Client(object):
    def __init__(self, url, apikey, secretkey):
        self.conn = CloudStackAdminDriver(url=url, key=apikey, secret=secretkey)

    def get_vlaniprange(self, uuid):
        ranges = self.conn.list_vlanipranges()
        return ranges[uuid]

    def get_vms(self, podid):