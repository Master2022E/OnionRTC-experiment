# OnionRTC-experiment
This project is a collection of the documentation, tools and scripts used for the experiment done in the DTU master project *"Improving anonymity in the use of TURN servers"* by Jonas T. Thomsen (s174867) and Christian A. S. Mark (s164833). 

The project is about investigating performance and usability of onion routing technologies like Tor, I2P and Lokinet for proxying WebRTC traffic.

# General overview of the experiment 
The experiment is visuallized in the diagram below and are made up of several hosts and components.
The application services are a collection of WebRTC specific infrastructure and central components, which enables hosting a WebRTC application, logging facilities, connection candidate signalling and "Traversal Using Relays around NAT" (TURN). These services are required for the experiment, and are hosted facing the public internet (Links to specific software packages can see in the next chapter with a small description).

Each communication line is explained here:

0.  Central Control server communicate with the two client hosts that they should start the experiment. 
1.  Central Control server signals to the logging server, that a test is starting with the two clients.
2.  The two clients goes to https://thomsen-it.dk and contacts the web server. A website is served, which the clients use to access a meeting room where they wait.
3.  Both of the clients contacts the signalling server, upgrades the connection to a WebSocket connection and start the discovery and negotiation process. Both clients start the [ICE](https://developer.mozilla.org/en-US/docs/Glossary/ICE) (Interactive Connectivity Establishment) protocol to exchange networking options and exchange session descriptors using [SDP](https://developer.mozilla.org/en-US/docs/Glossary/SDP) (Session Description Protocol). Both clients are setup to only use TURN over tcp, so they both exchange ICE candidates using the TURN server.
4.   To start sending video and audio data, both clients contacts the TURN server and gets allocated their own TCP communication port. The two clients will now be connected through the TURN server, which acts as a relay and sends data to each client. The data being send is rtp and rtcp, which is wrapped in encrypted tcp/TLS.
5.   Last but not least, all the statistics gathered from the WebRTC clients is sent to the logging server. This include: timestamps, RTT, jitter, packetloss,  and other metrics.   



![](overview.drawio.svg)


# Software used for the experiment

This table contains a component name, software package/reporsitory, a description and a link for getting the software.

| **Component name**     | **Used for**                                                                                                                                                      | **software package/reporsitory** | **Link(s)**                                      |
|------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------|--------------------------------------------------|
| Web server             | Hosting a website serving HTML and javascript to facilitate/bootstrap a WebRTC session.                                                                           | Simple WebRTC                    | https://github.com/Master2022E/simple-webrtc     |
| TURN server            | Providing "Traversal Using Relays around NAT" for WebRTC clients behind a strict NAT..                                                                            | coturn                           | https://github.com/coturn/coturn                 |
| Signalling server      | Provides clients of the Web server ability to plan and exchange connection/communication information.                                                             | Signal Server                    | https://github.com/Master2022E/SignalServer      |
| Central control server | Server that start the experiment by talking to the two client hosts and logging server.                                                                           | tdb                              | tbd                                              |
| Logging server         | Provide a central logging endpoint for "Central control server" and WebRTC clients .                                                                              | tbd                              | tbd                                              |
| Onion routing (Tor)    | Provide an anonymity proxy through the TOR network, which tunnels all HTTPs and WebRTC traffic.                                                                   | Tor                              | https://support.torproject.org/apt/#tor-deb-repo |
| Host browser           | Browser automation tool that will start a WebRTC session on a client host. It is activated by the Central control server and send its logs to the logging server. | Selenium                         | https://www.selenium.dev/                        |


# Experiment details



Take your TURN.