# Mongo DB Cheat Sheet

Create a local ssh port forward: `ssh -L 27017:127.0.0.1:27017 agpbruger@db.thomsen-it.dk -p 22022`

For local development the database data can be downloaded from [OneDrive](https://dtudk-my.sharepoint.com/:f:/g/personal/s174867_dtu_dk/EsRd292i0dNAsrAovfA3g_sBByGImHEglCYv2f_PayRAhg?e=KqzwQ4)

Extract to the folder `./database/db` and then run the command below to start the docker-compose mongo database.

## Small query commands

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