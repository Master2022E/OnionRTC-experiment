#!/bin/bash 

######## Tor part
# From their own guide: https://support.torproject.org/apt/tor-deb-repo/
# but we can't seem to make it work. So we just use the one installed via apt

sudo apt update
sudo apt install tor

test -e /etc/tor/torrc || (echo "/etc/tor/torrc was not found, do you have Tor installed in the correct folder?" && exit)

echo 'Look in the script for the different options for the torrc file'
# Depending on the Tor Setup add these as a new lines in the torrc file below


#echo "
#EntryNodes {dk},{se},{no},{fi},{de},{fr},{be},{nl},{pl},{cz},{lu},{lv},{ee},{ch},{gb} StrictNodes 1
#MiddleNodes {dk},{se},{no},{fi},{de},{fr},{be},{nl},{pl},{cz},{lu},{lv},{ee},{ch},{gb} StrictNodes 1
#ExitNodes {dk},{se},{no},{fi},{de},{fr},{be},{nl},{pl},{cz},{lu},{lv},{ee},{ch},{gb} StrictNodes 1
#HashedControlPassword 16:57DE65B9EFE2F2DE6023D7E90AA9E0C93F08E2636B07C7678985388B9D
#ControlPort 9051" | sudo tee -a /etc/tor/torrc
#
#echo "
#EntryNodes {dk},{se},{no},{fi} StrictNodes 1
#MiddleNodes {dk},{se},{no},{fi} StrictNodes 1
#ExitNodes {dk},{se},{no},{fi} StrictNodes 1 
#HashedControlPassword 16:57DE65B9EFE2F2DE6023D7E90AA9E0C93F08E2636B07C7678985388B9D
#ControlPort 9051" | sudo tee -a /etc/tor/torrc
#
#echo "
#HashedControlPassword 16:57DE65B9EFE2F2DE6023D7E90AA9E0C93F08E2636B07C7678985388B9D
#ControlPort 9051" | sudo tee -a /etc/tor/torrc


# Restart Tor so it uses the new torrc config and verify that Tor is running
#sudo systemctl restart tor
#sudo systemctl status tor

# You can verify that Tor uses the new config by installing and running: sudo nyx
# or by running:
# curl --socks5-hostname localhost:9050 https://check.torproject.org | grep 'You are not using Tor\| Congratulations. This browser is configured to use Tor'
# And verify that you get two different IP addresses when running:
# curl -s --socks5-hostname 127.0.0.1:9050 ifconfig.me
# curl ifconfig.me
