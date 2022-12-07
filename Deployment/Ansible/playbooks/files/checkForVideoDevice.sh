#!/bin/bash
# Check for video device

if ls /dev/video0; then
    #echo "ls /dev/video0 returned true"
    exit 0
else
    #echo "ls /dev/video0 returned false"
    exit 1
fi