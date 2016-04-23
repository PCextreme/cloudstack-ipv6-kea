#!/usr/bin/env python3
"""
Print a Kea configuration file for ISC Kea to run with

It requires the original Kea configuration as input where it will
override the 'reservations' section in the configuration
"""

import cloudstack.kea
import json
import libcloud
import argparse
import logging
import os
import sys

LOGGER = logging.getLogger(__name__)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='CloudStack ISC Kea DHCPv6 '
                                                 'configuration generator')
    parser.add_argument("--config", action="store", dest="conffile",
                        default="config.json", help="Configuration file")
    parser.add_argument("--debug", action="store_true", dest="debug",
                        default=False, help="Turn debug on")
    args = parser.parse_args()

    if os.path.isfile(args.conffile) is False:
        LOGGER.error('%s is not a regular file', args.conffile)
