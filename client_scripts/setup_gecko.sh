#!/bin/bash
# Follows this guide https://askubuntu.com/questions/870530/how-to-install-geckodriver-in-ubuntu?noredirect=1&lq=1
# to install and setup the geckodriver in the /usr/bin/geckodriver

INSTALL_DIR="/usr/bin"

json=$(curl -s https://api.github.com/repos/mozilla/geckodriver/releases/latest) 
url=$(echo "$json" | jq -r '.assets[].browser_download_url | select(contains("linux64") and endswith("gz"))')
curl -s -L "$url" | tar -xz
chmod +x geckodriver
sudo mv geckodriver "$INSTALL_DIR"
echo "installed geckodriver binary in $INSTALL_DIR"
