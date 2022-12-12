#!/bin/bash
#sudo modprobe v4l2loopback devices=1 card_label="My Fake Webcam" exclusive_caps=1
#ffmpeg -stream_loop -1 -re -i ./BigBuckBunny.mp4 -vcodec rawvideo -pix_fmt yuv420p -threads 0 -f v4l2 /dev/video0 # Video only
echo "$PWD"
res1=$(date +%s.%N)


# https://unix.stackexchange.com/questions/193208/program-run-in-ssh-accessing-pulseaudio-on-the-machine-where-it-runs
# Disable authentication for PulseAudio, so we can run the pactl commands over ssh
# Can be installed via "sudo apt install pulseaudio-utils"
pax11publish -r
#pulseaudio --check -v
pulseaudio --kill
pulseaudio -D -vvv

cfg=${CLIENT_CONFIG:-NOT SET!}



# Video and audio?
pactl load-module module-null-sink sink_name="virtual_speaker" sink_properties=device.description="virtual_speaker"
pactl load-module module-remap-source master="virtual_speaker.monitor" source_name="virtual_mic" source_properties=device.description="virtual_mic"
#ffmpeg -stream_loop -1 -nostdin -re -i output1.mp4 -f v4l2 /dev/video0 & PULSE_SINK=virtual_speaker ffmpeg -stream_loop -1 -i output1.mp4 -f pulse "stream name"
ffmpeg -stream_loop -1 -nostdin -re -i /home/agpbruger/Documents/OnionRTC-experiment/client_scripts/BigBuckBunny.mp4 -vf "drawtext=x=0:y=8:box=1:fontcolor=yellow:fontsize=50:boxcolor=black:expansion=strftime:basetime=$(date +%s -d'00:00:00')000000:text='$newline Start\:%Y-%m-%d %H\\:%M\\:%S Cfg\: $cfg $newline'"  -f v4l2 /dev/video0 & PULSE_SINK=virtual_speaker ffmpeg -stream_loop -1 -i /home/agpbruger/Documents/OnionRTC-experiment/client_scripts/BigBuckBunny.mp4 -f pulse "stream name"
kill $!

echo -e "\n----------------------------------"
res2=$(date +%s.%N)
dt=$(echo "$res2 - $res1" | bc)
dd=$(echo "$dt/86400" | bc)
dt2=$(echo "$dt-86400*$dd" | bc)
dh=$(echo "$dt2/3600" | bc)
dt3=$(echo "$dt2-3600*$dh" | bc)
dm=$(echo "$dt3/60" | bc)
ds=$(echo "$dt3-60*$dm" | bc)

LC_NUMERIC=C printf "Total runtime: %d:%02d:%02d:%02.4f\n" $dd $dh $dm $ds
