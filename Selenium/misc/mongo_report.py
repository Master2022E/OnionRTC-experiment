from pymongo import MongoClient
from datetime import datetime
from dotenv import load_dotenv
import os
import json

"""
!pip install pymongo
!pip install pandas
"""

mongo_conn = None
logging_global = print


logging_str = ["NOT_SET","CLIENT_START","CLIENT_RUNNING", "CLIENT_END", "CLIENT_ERROR"]
logging_types = dict()
for type in logging_str:
    logging_types[type] = type


def setup_mongo_connection(logging=None):
    global logging_global
    if logging is not None:
        logging_global = logging.info
    else:
        logging_global = print
    address = f'mongodb://{os.getenv("MONGO_USER")}:{os.getenv("MONGO_PASSWORD")}@{os.getenv("MONGO_HOST")}:{os.getenv("MONGO_PORT")}'
    client = MongoClient(address)
    
    return client

def close_mongo_connection():
    global mongo_conn
    if mongo_conn is not None:
        try:
            mongo_conn.close()
            mongo_conn = None
        except Exception as e:
            pass
            
def create_client_report(data:dict=dict(),logging=None):
    global mongo_conn
    global logging_types

    load_dotenv()
    if mongo_conn is None:
        mongo_conn = setup_mongo_connection(logging)


    
        
    database= mongo_conn["observertc-reports"]

    # the collection we want to query
    reportsDatabase = database.calls       

    data['timestamp'] = str(datetime.now())
    data["logging_type"] = logging_types[data.get("logging_type","NOT_SET")]

    try:
        reportsDatabase.insert_one(data)
        del data['_id'] # https://stackoverflow.com/questions/17529216/mongodb-insert-raises-duplicate-key-error
        logging_global(f'A {data.get("logging_type")} log was sent')
    except (KeyboardInterrupt, Exception) as e:
        logging_global("Error while sending logging data")
        logging_global(e)
        
    
if __name__ == "__main__":
    logging_str = ["NOT_SET","CLIENT_START","CLIENT_RUNNING", "CLIENT_END", "CLIENT_ERROR"]
    logging_types = dict()
    for type in logging_str:
        logging_types[type] = type
        
    data = {'client_username':'hej', "client_id": "client_id", "client_type": "client_type",
            "room_id": "room_id",
            "test_id": "test_id","logging_type": logging_types["CLIENT_START"]}

    create_client_report(data)

    data = {'client_username':'hej', "client_id": "client_id", "client_type": "client_type",
            "room_id": "room_id",
            "test_id": "test_id","logging_type": logging_types["CLIENT_ERROR"], "error": "This is a test error"}
    create_client_report(data)

    close_mongo_connection()