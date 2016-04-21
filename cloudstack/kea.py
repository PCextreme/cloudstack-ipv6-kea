"""
Class to generate a Kea configuration based on the CloudStack database
"""

class Kea(object):
    """
    This class generates a Kea configuration based on information in the
    CloudStack MySQL database.

    The class needs to be instantiated with a open (Read-Only) MySQL connection
    after which it can use this to generate the configuration for Kea.

    The mapping has to be a dict which maps `vlan`.`uuid` to:
    - Kea 'interface-id'
    - /40 subnet

    The mapping is a list which should look like this:

    [
      '7f5bddc3-b218-421e-911e-0257a41a9ca6': {
                                                'subnet': '2a00:f10:305::/64',
                                                'pool': '2a00:f10:500::/40',
                                                'interface-id': 'VLAN709'
                                              },
      '2a82ac9c-ef93-47c9-84c2-48e42f22b62a': {
                                                'subnet': '2a00:f10:400::/64',
                                                'pool': '2a00:f10:600::/40',
                                                'interface-id': 'VLAN701'
                                              }
    ]
    """
    def __init__(self, conn, mapping):
        self._conn = conn
        self._mapping = mapping

    def get_mapping(self, uuid):
        """
        Get the mapping delclaration for a VLAN UUID
        """
        return self._mapping[uuid]

    def get_kea_configuration(self, config):
        """
        Return a dict with Kea configuration

        As an argument it requires the existing Kea configuration as a dict
        where it will only add the reservations.

        The rest of the configuration will stay untouched
        """
        return config
