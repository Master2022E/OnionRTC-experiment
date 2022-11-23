from pymongo import MongoClient
from datetime import datetime
from dotenv import load_dotenv
import os
import json
import pandas as pd

"""
!pip install pymongo
!pip install pandas
"""


def setup_mongo_connection():
    address = f'mongodb://{os.getenv("MONGO_USER")}:{os.getenv("MONGO_PASSWORD")}@{os.getenv("MONGO_HOST")}:{os.getenv("MONGO_PORT")}'
    client = MongoClient(address)
    return client


def create_client_report(data:dict=dict()):
    load_dotenv()
    mongo_conn = setup_mongo_connection()

    logging_str = ["NOT_SET","CLIENT_START","CLIENT_RUNNING", "CLIENT_END", "CLIENT_ERROR"]
    logging_types = dict()
    for type in logging_str:
        logging_types[type] = type

    with mongo_conn as client:
        
        database= client["observertc-reports"]

        # the collection we want to query
        reportsDatabase = database.calls       

        # Timestamp, client_username, client_id, client_type, room_id, test_id, logging_type
        data = {'timestamp': str(datetime.now()), 'client_username': data.get('client_username','client_username'),
        'client_id': data.get('client_id','client_id'), 'client_type': data.get('client_type','client_type'),
        'room_id': data.get("room_id","room_id"), 
        "test_id":data.get("test_id","test_id"), "logging_type": logging_types[data.get("logging_type","NOT_SET")]}

        try:
            reportsDatabase.insert_one(data)
        except (KeyboardInterrupt, Exception) as e:
            print("Error while processing data")
            print(e)
        
    
if __name__ == "__main__":
    logging_str = ["NOT_SET","CLIENT_START","CLIENT_RUNNING", "CLIENT_END", "CLIENT_ERROR"]
    logging_types = dict()
    for type in logging_str:
        logging_types[type] = type
        
    data = {'client_username':'hej', "client_id": "client_id", "client_type": "client_type",
            "room_id": "room_id",
            "test_id": "test_id","logging_type": logging_types["CLIENT_START"]}

    create_client_report(data)