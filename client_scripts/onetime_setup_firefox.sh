#!/bin/bash 

# ###### Firefox part: We need to uninstall the standard version installed from snap and install a version from apt.
# This seems to be because of how snap sandboxes the app and how the geckodriver uses firefox.
# https://www.omgubuntu.co.uk/2022/04/how-to-install-firefox-deb-apt-ubuntu-22-04#:%7E:text=Installing%20Firefox%20via%20Apt%20(Not%20Snap)

sudo snap remove firefox

sudo add-apt-repository ppa:mozillateam/ppa

# This seems to ask for "Enter" promt when ran, maybe look into alternativ if the script should be automated!
echo '
Package: firefox*
Pin: release o=LP-PPA-mozillateam
Pin-Priority: 1001
' | sudo tee /etc/apt/preferences.d/mozilla-firefox

sudo apt install -y firefox