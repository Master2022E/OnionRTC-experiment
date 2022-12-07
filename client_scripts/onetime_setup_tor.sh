#!/bin/bash 

######## Tor part
# From their own guide: https://support.torproject.org/apt/tor-deb-repo/

sudo apt install apt-transport-https
sudo touch /etc/apt/sources.list.d/tor.list
sudo echo "deb     [signed-by=/usr/share/keyrings/tor-archive-keyring.gpg] https://deb.torproject.org/torproject.org stretch main
   deb-src [signed-by=/usr/share/keyrings/tor-archive-keyring.gpg] https://deb.torproject.org/torproject.org stretch main
" | sudo tee -a /etc/apt/sources.list.d/tor.list

wget -qO- https://deb.torproject.org/torproject.org/A3C4F0F979CAA22CDBA8F512EE8CBC9E886DDD89.asc | gpg --dearmor | sudo tee /usr/share/keyrings/tor-archive-keyring.gpg >/dev/null

# If you encounter an error saying:
# "Some packages could not be installed. This may mean that you have
# requested an impossible situation or if you are using the unstable
# distribution that some required packages have not yet been created
# or been moved out of Incoming.
# The following information may help to resolve the situation:
# 
# The following packages have unmet dependencies:
#  tor : Depends: libevent-2.0-5 (>= 2.0.10-stable) but it is not installable
#        Depends: libssl1.1 (>= 1.1.0) but it is not installable
#        Recommends: tor-geoipdb but it is not going to be installed
#        Recommends: torsocks but it is not going to be installed
# E: Unable to correct problems, you have held broken packages."
# you can fix it here: https://askubuntu.com/questions/563178/the-following-packages-have-unmet-dependencies

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


# Restart Tor so it uses the new torrc config and verify that Tor is running
sudo systemctl restart tor
sudo systemctl status tor

# You can verify that Tor uses the new config by installing and running: sudo nyx