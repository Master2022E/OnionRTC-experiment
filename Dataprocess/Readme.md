# Data processing

To get data ready for processing, run the [ExtractRawData.ipynb](./ExtractRawData.ipynb) notebook. This will connect to the MongoDB instance and gather the call stats, do som basic data transformation and save it to a CSV file which will be appended to each time the script is called.

## Single call statistics

The notebook [SingleCallStatistics](./SingleCallStatistics.ipynb) can from a `roomId` give detailed statistics of the calls in the given room.

## Call Statistics

This is TODO. But will point to a notebook where all calls measured will be summarized by different scenarios and their call quality.


---

> WARN The docker image have not been tested yet.