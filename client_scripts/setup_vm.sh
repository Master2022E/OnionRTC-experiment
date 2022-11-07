#!/bin/bash

## declare an array variable
declare -a arr=("git --version" "ffmpeg -version" "tor --version" "jq --version" "curl --version" "pip --version")

"""
sudo apt -y install python3-pip jq curl git ffmpeg libcurl4-openssl-dev libssl-dev htop net-tools vim nyx

Tor should be installed manually: 
For pycurl: sudo apt install libcurl4-openssl-dev libssl-dev
"""


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