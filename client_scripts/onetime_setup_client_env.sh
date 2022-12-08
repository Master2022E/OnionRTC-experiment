#!/bin/bash
# can be "Tor", "I2P", "Lokinet" or "None"
# you can also use the Selenium/.envExample file to set this

echo 'export CLIENT_CONFIG="Tor"' >> ~/.bashrc
#update current shell
source ~/.bashrc

echo $CLIENT_CONFIG
