#!/usr/bin/python3
import argparse
import logging
import os
import subprocess

from helpers.os_tools import *
from helpers.config_handler import *

# Checks if running as root and elevates if not
elevate_privileges()
config = ConfigHandler('/opt/RuneScripts/config.json')

# Argument Parsing
parser = argparse.ArgumentParser(description='Update RuneScripts scripts from the repository.')
args = parser.add_argument('-d', '--domain', type=str, help='Domain to expose the service on')
args = parser.add_argument('-p', '--port', type=int, help='Port to expose the service on')
args = parser.add_argument('-n', '--name', type=str, help='Name of the service to expose (will be used for filename)')
args = parser.add_argument('-v','--verbose', action='store_true', help='Enable verbose output')
parsed_args = parser.parse_args()

# Set logging level
if parsed_args.verbose:
    logging.getLogger().setLevel(logging.DEBUG)
