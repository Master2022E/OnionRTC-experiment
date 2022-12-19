# Data processing

> NOTE: To access the Mongo database locally, it's a requirement to create a local port forward though ssh. Like: `ssh -L 27017:127.0.0.1:27017 agpbruger@db.thomsen-it.dk -p 22022
`

To get data ready for processing, run the [ExtractRawData.ipynb](./ExtractRawData.ipynb) notebook. This will connect to the MongoDB instance and gather the call stats, do som basic data transformation and save it to a CSV file which will be appended to each time the script is called.

## Single call statistics

The notebook [SingleCallStatistics](./SingleCallStatistics.ipynb) can from a `roomId` give detailed statistics of the calls in the given room.

## Call Statistics

This is TODO. But will point to a notebook where all calls measured will be summarized by different scenarios and their call quality.

### Scenario list

One to one.

1. `Alice` &rarr; `Turn` &larr; `Bob`
2. `Alice` &rarr; `Tor (World)` &rarr; `Turn` &larr; `Tor (World)` &larr; `Bob`
3. `Alice` &rarr; `Tor (Europe)` &rarr; `Turn` &larr; `Tor (Europe)` &larr; `Bob`
4. `Alice` &rarr; `Tor (Scandinavia)` &rarr; `Turn` &larr; `Tor (Scandinavia)` &larr; `Bob`
5. `Alice` &rarr; `I2P` &rarr; `Turn` &larr; `I2P` &larr; `Bob`
6. `Alice` &rarr; `Lokinet` &rarr; `Turn` &larr; `Lokinet` &larr; `Bob`

Normal to Anonymized

7. `Alice` &rarr; `Turn` &larr; `Tor (World)` &larr; `Bob`
8. `Alice` &rarr; `Turn` &larr; `Tor (Europe)` &larr; `Bob`
9. `Alice` &rarr; `Turn` &larr; `Tor (Scandinavia)` &larr; `Bob`
10. `Alice` &rarr; `Turn` &larr; `I2P` &larr; `Bob`
11. `Alice` &rarr; `Turn` &larr; `Lokinet` &larr; `Bob`

Tor to Tor

12. `Alice` &rarr; `Tor (World)` &rarr; `Turn` &larr; `Tor (Europe)` &larr;`Bob`
13. `Alice` &rarr; `Tor (World)` &rarr; `Turn` &larr; `Tor (Scandinavia)` &larr;`Bob`
14. `Alice` &rarr; `Tor (Europe)` &rarr; `Turn` &larr; `Tor (Scandinavia)` &larr;`Bob`

For each test call will there be added logs to MongoDb for what setup was started and each client will log what setup it is configured to use.

---

> WARN The docker image have not been tested yet.