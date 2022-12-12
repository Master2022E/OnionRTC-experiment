# Command and Control

The program will be in charge of staring the tests between clients.

## Setup

The program will run on server A, see the [Deployment diagram](../Deployment/).

To allow local development with connections to the Mongo database, it is needed to create a local port forward.

```shell
ssh -L 27017:127.0.0.1:27017 agpbruger@db.thomsen-it.dk -p 22022
```