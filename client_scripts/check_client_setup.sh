#!/bin/bash

env_file='/home/'${USER}'/OnionRTC-experiment/Selenium/.env'

if [ ! -f $env_file ]; then
    echo "Env file '${env_file}' not found!"
    exit 1
fi

env_file='/home/'${USER}'/OnionRTC-experiment/Selenium/misc/.env'

if [ ! -f $env_file ]; then
    echo "Env file '${env_file}' not found!"
    exit 1
fi


env_file='/home/'${USER}'/OnionRTC-experiment/Selenium/misc/Tor/.env'

if [ ! -f $env_file ]; then
    echo "Env file '${env_file}' not found!"
    exit 1
fi

key_file='/home/'${USER}'/.ssh/id_ecdsa'

if [ ! -f $key_file ]; then
    echo "Key file '${key_file}' not found!"
    exit 1
fi

# Check if the key can be used for SSH tunnel to MongoDB
_HOST=stage.thomsen-it.dk
ssh -q -o BatchMode=yes  -o StrictHostKeyChecking=no -i $key_file $_HOST -p 22022 'exit 1'
_RCODE=$?
if [ $_RCODE -ne 0 ]
then
    echo "unable to ssh, host is not accessible"
else
    echo "ssh tunnel to mongoDB server is working"
fi

groups | grep video >> /dev/null
_RCODE=$?
if [ $_RCODE -ne 0  ]
then
    echo "User is not added to the video group - please run 'sudo systemctl restart webcam.service && journalctl -u webcam.service -f'"
else
    echo "User is added to the video group"
fi


service_file='/etc/systemd/system/webcam_permission.service'

if [ ! -f $service_file ]; then
    echo "Service file '${service_file}' not found!"
    exit 1
fi
systemctl is-enabled --quiet webcam_permission.service && echo webcam_permission.service is enabled || (echo webcam_permission.service is not enabled; exit 1)

service_file2='/etc/systemd/system/webcam.service'

if [ ! -f $service_file2 ]; then
    echo "Service file '${service_file2}' not found!"
    exit 1
fi

systemctl is-enabled --quiet webcam.service && echo webcam.service is enabled || (echo webcam.service is not enabled; exit 1)
systemctl is-active --quiet webcam.service && echo Service is running || (echo webcam.service is not running; exit 1)


# Does the webcam seem to work?
# If v4l2-ctl is installed
if ls /dev/video0; then
    echo "ls /dev/video0" returned true
else
    echo "ls /dev/video0" returned false
    exit 1
fi

# Check that the correct firefox installation is installed
if ! command -v firefox &> /dev/null
then
    echo "firefox could not be found"
    exit
fi

firefox_installation="$(which firefox)"
correct_installation="/usr/bin/firefox"
wrong_installation="/snap/bin/firefox"

if [ $firefox_installation == $correct_installation ]; then
    echo "Firefox installation seems correct"
else
    echo "Firefox installation does not seem correct"
    if [ $firefox_installation == $wrong_installation ]; then
        echo "Firefox seems to be installed with snap, please install it with apt!"
    fi
    exit 1
fi
sudo usermod -a -G video ${USER}