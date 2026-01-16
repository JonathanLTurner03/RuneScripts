#!/usr/bin/python3
import sys
import logging
import os
import subprocess

from helpers.os_tools import *

# Checks if running as root and elevates if not
elevate_privileges()

# Argument Parsing
if len(sys.argv) > 1:
    port = sys.argv[1]
else:
    print("No port provided. Exiting.")
    print("Usage: check-port.py <port> (e.g., 8080)")
    exit(1)

print(f'Checking if port {port} is in use...')

# Sanitize port input
try:
    port = int(port)
    if port < 1 or port > 65535:
        raise ValueError
except ValueError:
    print("Invalid port number. Please provide a port between 1 and 65535.")
    exit(1)
except TypeError:
    print("Port must be an integer.")
    exit(1)


# Check if the port is in use
(is_used, process) = check_port_in_use(port)
if is_used:
    print(f'Port {port} is currently in use by process: {process}')
else:
    print(f'Port {port} is free and not in use.')