#!/bin/bash

## declare an array variable
declare -a arr=("git --version" "ffmpeg -version" "tor --version" "jq --version" "curl --version" "pip --version")

# For installing everything run:
sudo apt -y install python3-pip jq curl git ffmpeg libcurl4-openssl-dev libssl-dev htop net-tools vim v4l2loopback-dkms v4l2loopback-utils linux-modules-extra-$(uname -r) pulseaudio pulseaudio-utils
# For Tor, you can also install nyx

# https://stackoverflow.com/questions/8880603/loop-through-an-array-of-strings-in-bash
## now loop through the above array
for i in "${arr[@]}"
do
    if ! command -v $i &> /dev/null
    then
        echo "'${i%% *}' could not be found. Please install"
        exit
    fi
done

# Setup video scripts
chmod +x ./*.sh
./get_bigbunny_video.sh





echo "All good"
