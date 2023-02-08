# Data Access

The data can be access in two ways.

1. Direct access though port forwarding
2. Local data access though self hosting services

## Direct access

Create a local ssh port forward to MongoDB and Prometheus:

- `ssh -TNL 27017:127.0.0.1:27017 agpbruger@a.thomsen-it.dk -p 22022`
- `ssh -TNL 9090:127.0.0.1:9090 agpbruger@a.thomsen-it.dk -p 22022`

> Pre shared SSH keys is required.

## Local data access

The data can be downloaded for local development from [OneDrive](https://dtudk-my.sharepoint.com/:f:/g/personal/s174867_dtu_dk/EsRd292i0dNAsrAovfA3g_sBByGImHEglCYv2f_PayRAhg?e=KqzwQ4) or [Google Drive](https://drive.google.com/file/d/1lGClPik535XdkNC408TlBNL4s28d22vO/view?usp=share_link) until 2023-03-15.

> For download though OneDrive a DTU account is required.

1. Extract the Mongo files to `./database/db` and the Prometheus files to `./database/prom`

2. Copy the .envExample to .env and fill in the information.

3. Start the docker containers with `docker-compose up -d`.

## Mongo DB queries

```mongo
# Find all calls where a scenario exists
db.calls.find({scenario_type: {$exists: true}}, )

# Find all the latest calls
db.calls.find({scenario_type: {$exists: true, $ne: "scenario_type"}}, )
        .sort({timestamp: -1})

# Find a call from room id
db.calls
    .find({room_id: {$eq: "f0faddfb-71b2-4777-8ac2-fef6b6df53b0"}})
    .sort({timestamp: -1})
```
