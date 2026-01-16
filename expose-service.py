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
args = parser.add_argument('-S', '--ssl', action='store_true', help='Enable SSL for the exposed service')
args = parser.add_argument('-s', '--no-ssl', action='store_false', help='Disable SSL for the exposed service')
args = parser.add_argument('-u', '--update-ddns', action='store_true', help='(WIP) Updates DDNS config (cloudflare) and restarts service')
args = parser.add_argument('-v','--verbose', action='store_true', help='Enable verbose output')
parsed_args = parser.parse_args()

# Set logging level
if parsed_args.verbose:
    logging.getLogger().setLevel(logging.DEBUG)

# Clear the console
os.system('cls' if os.name == 'nt' else 'clear')

domain = parsed_args.domain
port = parsed_args.port
ssl = parsed_args.ssl if parsed_args.ssl is not None else parsed_args.no_ssl

# Domain Setup
if domain:
    logging.info(f'Selected domain: {domain}')
else:
    logging.debug('No domain provided...')
    domain = input('Enter the domain to expose the service on: ').strip()

# Check if Domain is resolving to another service on the machine (checks Apache configs)
apache_sites_available = '/etc/apache2/sites-available'
for filename in os.listdir(apache_sites_available):
    if filename.endswith('.conf'):
        with open(os.path.join(apache_sites_available, filename), 'r') as file:
            config_content = file.read()
            if f'ServerName {domain}' in config_content:
                logging.warning(f'The domain {domain} is already configured in Apache site: {filename}')
                input_choice = input('Do you want to continue anyway? (y/n): ').strip().lower()
                if input_choice != 'y':
                    logging.error('Exiting... Domain conflict.')
                    exit(1)

# Port Setup
if port:
    logging.info(f'Setting up port: {port}')
else: 
    logging.debug('No port provided...')
    port_input = input('Enter the port to expose the service on (default 80): ').strip()
    port = int(port_input) if port_input else 80

# Check if port is already in use
(in_use, process) = check_port_in_use(port)
if in_use:
    logging.info(f'Port {port} is in use by process: {process}')
    input_choice = input(f'Is this the correct process? (y/n): ').strip().lower()
    if input_choice == 'y':
        logging.debug('Continued process is confirmed to be correct.')
    else: 
        logging.error(f'Exiting... Wrong port selected.')
        exit(1)

if parsed_args.name:
    service_name = parsed_args.name
else:
    service_name = input('Enter the name of the service (will be used for filename): ').strip()

# Check apache configs for existing config with same name
apache_config_path = f'/etc/apache2/sites-available/{service_name}.conf'
if os.path.exists(apache_config_path):
    logging.warning(f'An Apache configuration with the name {service_name} already exists.')
    input_choice = input('Do you want to overwrite it? (y/n): ').strip().lower()
    if input_choice != 'y':
        logging.error('Exiting... Configuration name conflict.')
        exit(1)

# SSL Setup
use_ssl = ssl
if use_ssl is not None:
    if use_ssl:
        logging.info('SSL will be enabled for the service.')
    else:
        logging.info('SSL will not be enabled for the service.')
else:
    ssl_input = input('Enable SSL for the service? (y/n, default n): ').strip().lower()
    use_ssl = ssl_input == 'y'

# Email Config Check
if config.get('admin_email') is None and use_ssl:
    email = input('Enter admin email for SSL certificate registration: ').strip()
    config.set('admin_email', email)

# Generate Apache Config using template provided in helpers/apache.conf
# Replaces ${DOMAIN}, ${NAME}, and ${PORT} placeholders in the template, and comments out the SSL lines (Lines 18-20) that way a2ensite can still be used 
apache_template_path = config.get('apache_template_path', '/opt/RuneScripts/helpers/apache.conf')
with open(apache_template_path, 'r') as template_file:
    apache_config = template_file.read()
apache_config = apache_config.replace('${DOMAIN}', domain)
apache_config = apache_config.replace('${NAME}', service_name)
apache_config = apache_config.replace('${PORT}', str(port))

# Comment out lines 18-20 so SSL can be enabled later if needed
apache_config_lines = apache_config.splitlines()
for i in range(len(apache_config_lines)):
    if i in [17, 18, 19]:  # Lines 18-20 (0-indexed)
        apache_config_lines[i] = f'# {apache_config_lines[i]}'
apache_config = '\n'.join(apache_config_lines)
with open(f'/etc/apache2/sites-available/{service_name}.conf', 'w') as config_file:
    config_file.write(apache_config)

# Setup SSL if needed
if use_ssl: 
    logging.info('Enabling SSL for the service...')
    subprocess.run(['a2enmod', 'ssl'])
    subprocess.run(['a2ensite', f'{service_name}.conf'])
    subprocess.run(['systemctl', 'reload', 'apache2'])
    logging.debug('Requesting SSL certificate from Let\'s Encrypt using Certbot...')
    logging.debug(f'Command: certbot --apache -d {domain} --non-interactive --agree-tos -m {config.get("admin_email")}')
    subprocess.run(['certbot', '--apache', '-d', domain, '--non-interactive', '--agree-tos', '-m', config.get('admin_email')])
    # Delete comment from lines 18-20 and delete certbot added lines 30-32
    with open(f'/etc/apache2/sites-available/{service_name}.conf', 'r') as config_file:
        apache_config = config_file.read()
        apache_config_lines = apache_config.splitlines()
        for i in range(len(apache_config_lines)):
            if i in [17, 18, 19]:  # Lines 18-20 (0-indexed)
                apache_config_lines[i] = apache_config_lines[i].lstrip('# ').rstrip()
            if i in [29, 30, 31]:  # Lines 30-32 (0-indexed)
                apache_config_lines[i] = ''
        apache_config = '\n'.join(apache_config_lines)
    with open(f'/etc/apache2/sites-available/{service_name}.conf', 'w') as config_file:
        config_file.write(apache_config)
else:
    subprocess.run(['a2ensite', f'{service_name}.conf'])
    subprocess.run(['systemctl', 'reload', 'apache2'])

logging.info(f'Exposing service on port {port} at domain {domain}. Configuration complete.')