#!/usr/bin/python3
import os
import subprocess
import argparse
import logging

from helpers.os_tools import *
from helpers.config_handler import *

# Checks if running as root and elevates if not
elevate_privileges()
config = ConfigHandler('/opt/RuneScripts/config.json')

# Argument Parsing
parser = argparse.ArgumentParser(description='Update RuneScripts scripts from the repository.')
args = parser.add_argument('-r', '--force-rebuild', action='store_true', help='Force rebuild of scripts even if up to date')
args = parser.add_argument('-f', '--force-update', action='store_true', help='Force update of scripts even if up to date')
args = parser.add_argument('-v','--verbose', action='store_true', help='Enable verbose output')
parsed_args = parser.parse_args()

if parsed_args.verbose:
    logging.getLogger().setLevel(logging.DEBUG)

current_dir = get_current_directory()

# Checking Updates and Comparing Hashes
logging.info('Checking for updates...')

current_hash = config.get('current_hash', '')
repo_url = config.get('repo_url', '')
scripts_dir = config.get('scripts_dir', '')

logging.debug(f'Current Hash: {current_hash}')
logging.debug(f'Repo URL: {repo_url}')
logging.debug(f'Scripts Directory: {scripts_dir}')

# Change to scripts directory
logging.debug(f'Changing directory to scripts directory: {scripts_dir}')
change_directory(scripts_dir)

# Get latest commit hash from remote
logging.debug('Fetching latest commit hash from remote repository...')
result = subprocess.run(['git', 'ls-remote', repo_url, 'HEAD'], stdout=subprocess.PIPE)
latest_hash = result.stdout.decode('utf-8').split()[0]
logging.debug(f'Latest Hash: {latest_hash}')

performed_update = False

# If hashes differ, pull latest changes
if current_hash != latest_hash or parsed_args.force_update:
    logging.info('Update available. Pulling latest changes...')
    subprocess.run(['git', '-C', scripts_dir, 'pull'])
    logging.info('Update complete.')
    performed_update = True

if not performed_update and not parsed_args.force_rebuild and not parsed_args.force_update:
    logging.info('No updates available.')
    logging.info('No rebuild flags set. Exiting.')
    logging.debug(f'Returning to original directory: {current_dir}')
    change_directory(current_dir)
    exit(0)

# After updating, create bin symlinks and set permissions and executables and removes .py extensions
bin_dir = scripts_dir + '/bin'
create_directory(bin_dir)
for script in os.listdir(scripts_dir):
    script_path = os.path.join(scripts_dir, script)
    if os.path.isfile(script_path) and script.endswith('.py'):
        set_executable(script_path)
        symlink_path = os.path.join(bin_dir, script[:-3])
        logging.debug(f'Creating symlink for {script_path} at {symlink_path}')
        create_symlink(script_path, symlink_path)

logging.info('Symlinks created and permissions set.')
logging.debug(f'Returning to original directory: {current_dir}')
change_directory(current_dir)