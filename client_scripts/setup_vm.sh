#!/bin/bash

## declare an array variable
declare -a arr=("git --version" "ffmpeg -version" "tor --version")

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