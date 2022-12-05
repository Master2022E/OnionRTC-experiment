# Host C and D - Client

The purpose of the client is to act as a client for the application. The client is responsible for connecting to the TURN server and the application server. Furthermore, the client is responsible for sending and receiving media. They are controlled by the "C&C" server over ssh and needs internet access.


![Deployment](../HostCD-Router/HostCD-deployment.drawio.svg)

## Setup
Each client has a specific enviroment setup, which is described in the [client scripts folder](../../client_scripts/) as small scripts.

The client setup can be divided into two parts. The first part is responsible for setting up the client with a fake webcam running a test video with audio. The other part consist of the client environment variables, setting up the anonimity network connection and lastly the firefox browser setup, used by Selenium.


### Webcam setup
> **NOTE:** TODO


### Client environment variables
> **NOTE:** TODO


### Anonimity network connection setup
> **NOTE:** TODO

### Firefox browser setup
> **NOTE:** TODO



## Firewall Setup

The clients just need to have the ssh port open to be able to connect to the router. This is done by adding the following rule to the ufw firewall.

```shell
sudo ufw allow 22022 comment 'Allow SSH connections'
```
This gives the configuration like shown below.

```shell
sudo ufw status
Status: active

To                         Action      From
--                         ------      ----            
22022                      ALLOW IN    Anywhere                       
22022 (v6)                 ALLOW IN    Anywhere (v6) 
```
