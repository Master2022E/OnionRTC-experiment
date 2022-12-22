# Command and Control

The program will be in charge of staring the tests between clients.

## Setup

The program will run on server A, see the [Deployment diagram](../Deployment/).

To allow local development with connections to the Mongo database, it is needed to create a local port forward.

```shell
ssh -fTNL 27017:localhost:27017 agpbruger@db.thomsen-it.dk -p 22022
# or 
ssh -L 27017:127.0.0.1:27017 agpbruger@db.thomsen-it.dk -p 22022
```

## Build

```shell
docker-compose build
``` 

## Start the service

```shell
docker-compose up -d
``` 

## Release

To release the image it is possible to publish to docker hub with the following command and it will update the tag of latest image and the verison number.

```shell
make publish username=foo version=v0.0.0
```