# Mongo DB Cheat Sheet

Create a local ssh port forward: `ssh -L 27017:127.0.0.1:27017 agpbruger@db.thomsen-it.dk -p 22022`

## Small query commands

```mongo
# Find all calls where a scenario exists
db.calls.find({scenario_type: {$exists: true}}, )

# Find all the latest calls
db.calls.find({scenario_type: {$exists: true, $ne: "scenario_type"}}, )
        .sort({timestamp: -1})
```