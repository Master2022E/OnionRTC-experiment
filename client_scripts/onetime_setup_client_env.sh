#!/bin/bash
# can be "Tor", "I2P", "Lokinet" or "None"
# you can also use the Selenium/.envExample file to set this

echo 'export CLIENT_CONFIG="None"' >> ~/.bashrc
echo 'export CLIENT_CONFIG="Lokinet"' >> ~/.bashrc
echo 'export CLIENT_CONFIG="I2P"' >> ~/.bashrc
echo 'export CLIENT_CONFIG="Tor"' >> ~/.bashrc
#update current shell
source ~/.bashrc

echo $CLIENT_CONFIG
