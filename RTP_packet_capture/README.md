# Capturing non encrypted RTP packets from a WebRTC session
Following this [guide](https://blog.mozilla.org/webrtc/debugging-encrypted-rtp-is-more-fun-than-it-used-to-be/)
for setting up firefox (ff) or the same procedure for the ff geckodriver.   
You would want to set these logging settings:

```
Current Log Modules to timestamp,signaling:5,jsep:5,RtpLogger:5
The log file name to: /tmp/logs/moz.log
```
They can be set as env variables or from this [configuration](about:networking#logging) page in firefox.

Then you can start a webrtc session and find the log files that you set.
When you have found the log files you can use the command:

```shell
egrep '(RTP_PACKET|RTCP_PACKET)' moz.log | cut -d '|' -f 2 | cut -d ' ' -f 5- | text2pcap -D -n -l 1 -i 17 -u 1234,1235 -t '%H:%M:%S.' - rtp_packets.pcap
```

To obtain a pcap file with the RTP packets. The packets do not show any jitter or loss,
but it is possible to see the RTP headers.

The example packet file is from a webrtc session between a test client using ff and normal ff browser.
The ff test client browser was running on an ubuntu VM with the ff geckodriver.
The webrtc session was initiated from the normal ff browser.


