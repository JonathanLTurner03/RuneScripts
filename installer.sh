#!/bin/bash

# Checks if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root"
    exit 1
fi

# Installs necessary dependencies
apt update
apt install -y git python3 python3-pip apache2 certbot python3-certbot-apache
# Clones the RuneScripts repository
git clone https://github.com/JonathanLTurner03/RuneScripts.git /opt/RuneScripts
# Installs Python dependencies
pip3 install -r /opt/RuneScripts/requirements.txt
# Makes the main script executable
chmod +x /opt/RuneScripts/update-scripts.py

# change default config to config.json
if [ ! -f /opt/RuneScripts/config.json ]; then
    cp /opt/RuneScripts/default-config.json /opt/RuneScripts/config.json
fi

# Perform initial script update
python3 /opt/RuneScripts/update-scripts.py --force-update

echo "Installation complete. Please restart your terminal or run 'source /etc/bash.bashrc' to update your PATH."
exit 0