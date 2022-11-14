#!/bin/bash
#sudo modprobe v4l2loopback devices=1 card_label="My Fake Webcam" exclusive_caps=1
#ffmpeg -stream_loop -1 -re -i ./BigBuckBunny.mp4 -vcodec rawvideo -pix_fmt yuv420p -threads 0 -f v4l2 /dev/video0 # Video only


#https://github.com/umlaeute/v4l2loopback/issues/247
sudo modprobe -r v4l2loopback
sudo modprobe v4l2loopback exclusive_caps=1 max_buffers=2


# https://unix.stackexchange.com/questions/193208/program-run-in-ssh-accessing-pulseaudio-on-the-machine-where-it-runs
# Disable authentication for PulseAudio, so we can run the pactl commands over ssh
pax11publish -r

# Video and audio?
pactl load-module module-null-sink sink_name="virtual_speaker" sink_properties=device.description="virtual_speaker"
pactl load-module module-remap-source master="virtual_speaker.monitor" source_name="virtual_mic" source_properties=device.description="virtual_mic"
#ffmpeg -stream_loop -1 -nostdin -re -i output1.mp4 -f v4l2 /dev/video0 & PULSE_SINK=virtual_speaker ffmpeg -stream_loop -1 -i output1.mp4 -f pulse "stream name"
ffmpeg -stream_loop -1 -nostdin -re -i BigBuckBunny.mp4 -vf "drawtext=x=8:y=8:box=1:fontcolor=yellow:fontsize=55:boxcolor=black:expansion=strftime:basetime=$(date +%s -d'00:00:00')000000:text='$newline %Y-%m-%d %H\\:%M\\:%S $newline'"  -f v4l2 /dev/video0 & PULSE_SINK=virtual_speaker ffmpeg -stream_loop -1 -i BigBuckBunny.mp4 -f pulse "stream name"
kill $!