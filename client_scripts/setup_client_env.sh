#!/bin/bash

echo 'export CLIENT_CONFIG="Tor"' >> ~/.bashrc
#update current shell
source ~/.bashrc

echo $CLIENT_CONFIG
