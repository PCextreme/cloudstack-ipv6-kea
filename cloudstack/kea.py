"""
Class to generate a Kea configuration based on the CloudStack database
"""

import ipaddress
from copy import deepcopy


class Kea(object):
    """
    This class generates a Kea configuration based on information in the
    CloudStack API.

    The mapping has to be a dict which mapping a VLAN UUID to:
    - Kea 'interface-id'
    - /40 subnet

    The mapping is a list which should look like this:

    [
      '7f5bddc3-b218-421e-911e-0257a41a9ca6': {
                                                'pool': '2a00:f10:500::/40',
                                                'interface-id': 'VLAN709'
                                              },
      '2a82ac9c-ef93-47c9-84c2-48e42f22b62a': {
                                                'pool': '2a00:f10:600::/40',
                                                'interface-id': 'VLAN701'
                                              }
    ]
    """
    def __init__(self, conn, mapping, config):
        self._conn = conn
        self._mapping = mapping
        self._config = config

    def get_mapping(self, uuid):
        """
        Get the mapping delclaration for a VLAN UUID
        """
        return self._mapping[uuid]

    def get_subnet_config(self, subnet):
        try:
            for entry in self._config['Dhcp6']['subnet6']:
                if entry['subnet'] == subnet:
                    return entry
        except KeyError:
            pass

    @staticmethod
    def find_next_prefix(reservations, pool, prefix_len):
        pool = ipaddress.ip_network(pool)
        subnets = pool.subnets(prefixlen_diff=(prefix_len - pool.prefixlen))

        while True:
            subnet = next(subnets).with_prefixlen
            try:
                subnet = reservations.index(subnet)
            except ValueError:
                return subnet

        return None

    @staticmethod
    def get_reservations(reservations):
        subnets = []
        for reservation in reservations:
            subnets.append(reservation['prefix'])

        return subnets

    @staticmethod
    def get_vm_reservation(reservations, hwaddr):
        try:
            for reservation in reservations:
                if reservation['hw-address'] == hwaddr:
                    return reservation
        except:
            pass

    def get_kea_configuration(self):
        """
        Return a dict with Kea configuration

        As an argument it requires the existing Kea configuration as a dict
        where it will only add the reservations.

        The rest of the configuration will stay untouched
        """

        """
        Copy the loaded configuration and drop all subnet declarations in it
        """
        config = deepcopy(self._config)
        config['Dhcp6']['subnet6'] = []

        for uuid, mapping in self._mapping.items():
            range = self._conn.get_vlaniprange(uuid)
            rangecfg = (self.get_subnet_config(range['ip6cidr']))

            if rangecfg is None:
                rangecfg = {'subnet': range['ip6cidr'], 'reservations': []}

            vms = self._conn.get_vms(range['podid'])

            reservations = []
            try:
                reservations = self.get_reservations(rangecfg['reservations'])
            except KeyError:
                pass

            rangecfg['reservations'] = []

            """
            For each VM we look for an existing reservation in the subnet

            If none is found we will look for a new prefix in that subnet
            """
            for vm in vms:
                macaddr = vm['nic'][0]['macaddress']
                reservation = self.get_vm_reservation(reservations, macaddr)

                if reservation is not None:
                    rangecfg['reservations'].append(reservation)
                else:
                    prefix = self.find_next_prefix(reservations, mapping['pool'],
                                                   mapping['prefix-len'])
                    rangecfg['reservations'].append({'hw-address': macaddr,
                                                     'prefix': prefix})

                rangecfg['interface-id'] = mapping['interface-id']
                rangecfg['reservation-mode'] = 'out-of-pool'

            config['Dhcp6']['subnet6'].append(rangecfg)

        return config
