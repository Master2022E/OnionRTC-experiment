#!/bin/bash
# This script is run once to add the user to the video group,
# so the ffmpeg webcam scripts can access the /dev/video0
sudo usermod -a -G video ${USER}