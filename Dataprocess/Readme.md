# Data processing

> NOTE: To access the Mongo database locally, it's a requirement to create a local port forward though ssh. Like: `ssh -L 27017:127.0.0.1:27017 agpbruger@db.thomsen-it.dk -p 22022
`

To get data ready for processing, run the [ExtractRawData.ipynb](./ExtractRawData.ipynb) notebook. This will connect to the MongoDB instance and gather the call stats, do som basic data transformation and save it to a CSV file which will be appended to each time the script is called.

## Single call statistics

The notebook [SingleCallStatistics](./SingleCallStatistics.ipynb) can from a `roomId` give detailed statistics of the calls in the given room.

## Call Statistics

This is TODO. But will point to a notebook where all calls measured will be summarized by different scenarios and their call quality.

### Scenario list

The client will be configured to use one of the following setups:

Networking type   | abbreviation
---               | ---
Normal            | Norm
Tor (Normal)      | TorN
Tor (Europe)      | TorE
Tor (Scandinavia) | TorS
Lokinet           | Loki

One to one.

1.  `Alice` &rarr; `Norm` &rarr; `Turn` &larr; `Norm` &larr; `Bob`
2.  `Alice` &rarr; `TorN` &rarr; `Turn` &larr; `TorN` &larr; `Bob`
3.  `Alice` &rarr; `TorE` &rarr; `Turn` &larr; `TorE` &larr; `Bob`
4.  `Alice` &rarr; `TorS` &rarr; `Turn` &larr; `TorS` &larr; `Bob`
5.  `Alice` &rarr; `Loki` &rarr; `Turn` &larr; `Loki` &larr; `Bob`

Normal to Anonymized in pairs

6.  `Alice` &rarr; `Norm` &rarr; `Turn` &larr; `TorN` &larr; `Bob`
7.  `Alice` &rarr; `Norm` &rarr; `TorN` &rarr; `Turn` &larr; `Bob`
8.  `Alice` &rarr; `Norm` &rarr; `Turn` &larr; `TorE` &larr; `Bob`
9.  `Alice` &rarr; `Norm` &rarr; `TorE` &rarr; `Turn` &larr; `Bob`
10. `Alice` &rarr; `Norm` &rarr; `Turn` &larr; `TorS` &larr; `Bob`
11. `Alice` &rarr; `Norm` &rarr; `TorS` &rarr; `Turn` &larr; `Bob`
12. `Alice` &rarr; `Norm` &rarr; `Turn` &larr; `Loki` &larr; `Bob`
13. `Alice` &rarr; `Norm` &rarr; `Loki` &rarr; `Turn` &larr; `Bob`


Tor to Tor in pairs

14. `Alice` &rarr; `TorN` &rarr; `Turn` &larr; `TorE` &larr; `Bob`
15. `Alice` &rarr; `TorE` &rarr; `Turn` &larr; `TorN` &larr; `Bob`
16. `Alice` &rarr; `TorN` &rarr; `Turn` &larr; `TorS` &larr; `Bob`
17. `Alice` &rarr; `TorS` &rarr; `Turn` &larr; `TorN` &larr; `Bob`
18. `Alice` &rarr; `TorE` &rarr; `Turn` &larr; `TorS` &larr; `Bob`
19. `Alice` &rarr; `TorS` &rarr; `Turn` &larr; `TorE` &larr; `Bob`

For each test call will there be added logs to MongoDb for what setup was started and each client will log what setup it is configured to use.

---

> WARN The docker image have not been tested yet.

## Results

The total success and failure rate of the calls can be seen in the [SuccessOrFail](./SuccessOrFail.ipynb) notebook.

And currently provides the following graph:

![Success or fail](./output_folder/SuccessOrFail.svg)

The success rate over time can be seen in the [SuccessRateOverTime](./SuccessRateOverTime.ipynb) notebook.

And currently provides the following graph:

![Success rate over time](./output_folder/SuccessRateOverTime.svg)