#!/bin/bash 

######## Tor part
# From their own guide: https://support.torproject.org/apt/tor-deb-repo/

sudo apt install apt-transport-https
sudo touch /etc/apt/sources.list.d/tor.list
sudo echo "deb     [signed-by=/usr/share/keyrings/tor-archive-keyring.gpg] https://deb.torproject.org/torproject.org stretch main
   deb-src [signed-by=/usr/share/keyrings/tor-archive-keyring.gpg] https://deb.torproject.org/torproject.org stretch main
" >> /etc/apt/sources.list.d/tor.list

wget -qO- https://deb.torproject.org/torproject.org/A3C4F0F979CAA22CDBA8F512EE8CBC9E886DDD89.asc | gpg --dearmor | tee /usr/share/keyrings/tor-archive-keyring.gpg >/dev/null
sudo apt update
sudo apt install tor deb.torproject.org-keyring

test -e /etc/tor/torrc || (echo "/etc/tor/torrc was not found, do you have Tor installed in the correct folder?" && exit)

# Depending on the Tor Setup add these as a new lines in the torrc file below
#ExitNodes {dk},{se} StrictNodes 1 
#MiddleNodes {dk},{se} StrictNodes 1
#EntryNodes {dk},{se} StrictNodes 1

echo "
HashedControlPassword 16:57DE65B9EFE2F2DE6023D7E90AA9E0C93F08E2636B07C7678985388B9D
ControlPort 9051" | sudo tee -a /etc/tor/torrc

