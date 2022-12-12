# Host B - Turn server

The purpose of the server is to host a Turn server that clients can use as a middel-man when having a online call.

## Setup

The folder [coturn](./coturn/) has an example configuration file. When the configuration file files have been configured, the service can be controlled with the makefile.

```shell
$ make

Options include:
  upload  - Uploads the local configuration files
  start   - Starts the services from docker-compose
  stop    - Stops the services from docker-compose
  restart - Stops and starts the services.
  status  - Get the status of the services
  pull    - Pulls the latest images of the services
  logs    - Get the latest 20 logs and follows the next logs
  ssh     - Gets an ssh shell on the server
```

## Services

### coturn

[coturn](https://github.com/coturn/coturn) is an open source implementation of a TURN server.

### Node Exporter

> TODO and might not happen. Will maybe be a weekend project.
[Node Exporter](https://github.com/prometheus/node_exporter) could give some easy insights to the load of the server. would be accessible on Host A.

## Initial setup

To run the application on the server are the applications [docker](https://www.docker.com/) and [docker-compose](https://docs.docker.com/compose/gettingstarted/) needed.

### Firewall

The turn service needs a lot of different ports opened to run the following rules is used

```shell
sudo ufw allow 22022 comment 'Allow SSH connections'
sudo ufw allow 3478 comment 'Turn'
sudo ufw allow 49152:65535/udp comment 'Turn'

```

This gives the configuration like shown below.

```shell
sudo ufw status
Status: active

To                         Action      From
--                         ------      ----
22022                      ALLOW       Anywhere                   # Allow SSH connections
3478                       ALLOW       Anywhere                   # Turn
49152:65535/udp            ALLOW       Anywhere                   # Turn
22022 (v6)                 ALLOW       Anywhere (v6)              # Allow SSH connections
3478 (v6)                  ALLOW       Anywhere (v6)              # Turn
49152:65535/udp (v6)       ALLOW       Anywhere (v6)              # Turn
```
