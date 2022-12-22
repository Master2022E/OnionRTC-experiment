import json
from pymongo import MongoClient
from dotenv import load_dotenv
import os
import time

# Loads the .env file from the local path
load_dotenv()

address = 'mongodb://{user}:{password}@{host}:{port}'.format(
    user=os.getenv('MONGO_USER'),
    password=os.getenv('MONGO_PASSWORD'),
    host=os.getenv('MONGO_HOST'),
    port=os.getenv('MONGO_PORT')
)

client = MongoClient(address)
database = client["observertc-reports"]

# the collection we want to query
db = database.reports

# print('connected to %s' % address)

cursor = db.find({"type": "CLIENT_EXTENSION_DATA",
                  "payload.extensionType": "OUT_BOUND_RTC"})


rooms = {}
for record in cursor:
    a = json.loads(record["payload"]["payload"])
    print(a)
    print(a["stats"]["type"])
    break
