#!/usr/bin/env python3
"""
Print a Kea configuration file for ISC Kea to run with

It requires the original Kea configuration as input where it will
override the 'reservations' section in the configuration
"""

import cloudstack.kea
import cloudstack.client
import json
import argparse
import logging
import os
import sys

LOGGER = logging.getLogger(__name__)

HANDLER = logging.StreamHandler(sys.stderr)
FORMATTER = logging.Formatter('%(asctime)s %(levelname)s %(name)s: %(message)s',
                              datefmt='%Y-%m-%dT%H:%M:%S%Z')
HANDLER.setFormatter(FORMATTER)
LOGGER.addHandler(HANDLER)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='CloudStack ISC Kea DHCPv6 '
                                                 'configuration generator')
    parser.add_argument("--config", action="store", dest="conffile",
                        default="config.json", help="Configuration file")
    parser.add_argument("--keacfg", action="store", dest="keacfg",
                        default="/etc/kea/kea-dhcp6.conf", help="Kea configuration file")
    parser.add_argument("--debug", action="store_true", dest="debug",
                        default=False, help="Turn debug on")
    args = parser.parse_args()

    try:
        config = json.loads(open(args.conffile, 'r').read())
        keacfg = json.loads(open(args.keacfg, 'r').read())

        client = cloudstack.client.Client(url=config['api']['url'],
                                          apikey=config['api']['apikey'],
                                          secretkey=config['api']['secretkey'])
        ranges = client.get_vlans_vms()
        kea = cloudstack.kea.Kea(ranges, config['mapping'], keacfg)
    except FileNotFoundError as exc:
        LOGGER.error('File does not exist: %s', exc)
        sys.exit(1)
    except PermissionError as exc:
        LOGGER.error('Failed to read config file: %s', exc)
        sys.exit(1)
    except (ValueError, KeyError) as exc:
        LOGGER.error('Failed to parse config file: %s', exc)
        sys.exit(1)

    try:
        keacfg = kea.get_kea_configuration()
        print(json.dumps(keacfg, indent=2))
    except Exception as exc:
        LOGGER.error('An error occured: %s', exc)
        sys.exit(1)
