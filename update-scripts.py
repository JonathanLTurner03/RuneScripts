#!/usr/bin/python3
import os
import subprocess
from helpers.os_tools import *
from helpers.config_handler import *

# Checks if running as root and elevates if not
elevate_privileges()
config = ConfigHandler('/opt/RuneScripts/config.json')

current_dir = get_current_directory()

# Checking Updates and Comparing Hashes
print('Checking for updates...')

current_hash = config.get('current_hash', '')
repo_url = config.get('repo_url', '')
scripts_dir = config.get('scripts_dir', '')

change_directory(scripts_dir)

result = subprocess.run(['git', 'ls-remote', repo_url, 'HEAD'], stdout=subprocess.PIPE)
latest_hash = result.stdout.decode('utf-8').split()[0]

performed_update = False

# If hashes differ, pull latest changes
if current_hash != latest_hash:
    print('Update available. Pulling latest changes...')
    subprocess.run(['git', '-C', scripts_dir, 'pull'])
    config.set('current_hash', latest_hash)
    print('Update complete.')
    performed_update = True

if not performed_update:
    print('No updates available.')
    print('No rebuild flags set. Exiting.')
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
        create_symlink(script_path, symlink_path)

print('Scripts are up to date and symlinks created.')
print(f'scripts_dir: {scripts_dir}')
change_directory(current_dir)