#!/bin/bash
#https://github.com/umlaeute/v4l2loopback/issues/247
sudo modprobe -r v4l2loopback
sudo modprobe v4l2loopback exclusive_caps=1 max_buffers=2