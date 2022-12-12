
from pymongo import MongoClient
from datetime import datetime
from dotenv import load_dotenv
import logging
import sys
import os

def _getCollection():
    """
    Returns the collection of calls in the mongo database
    """
    load_dotenv()
    address = f'mongodb://{os.getenv("MONGO_USER")}:{os.getenv("MONGO_PASSWORD")}@127.0.0.1:27017'
    client = MongoClient(address)
    database = client["observertc-reports"]
    return database["calls"]



def log( loggingType: str, data = dict(), test_id = None, room_id = None, client_id = None, client_username = None):
    """
    Sends a log to the mongo database

    Parameters
    ----------
    loggingType : str
        The type of logging to be done
    data : dict, optional
        The data to be logged, by default dict()
    test_id : str, optional
        The test id, by default None
    room_id : str, optional
        The room id, by default None
    client_id : str, optional
        The client id, by default None
    client_username : str, optional
        The client username, by default None
    """

    data['timestamp'] = str(datetime.now())
    data["logging_type"] = loggingType
    data["client_type"] = "CnC"

    if(test_id is not None):
        data["test_id"] = test_id
    if(room_id is not None):
        data["room_id"] = room_id
    if(client_id is not None):
        data["client_id"] = client_id
    if(client_username is not None):
        data["client_username"] = client_username

    # https://stackoverflow.com/questions/17529216/mongodb-insert-raises-duplicate-key-error
    if("_id" in data):
        del data['_id'] 

    try:
        collection = _getCollection()
        collection.insert_one(data)
        logging.info(f'A {data.get("logging_type")} log was sent')
    except (KeyboardInterrupt, Exception) as e:
        logging.error("Error while sending logging data", e)


if __name__ == "__main__":

    # Setup logging
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging.DEBUG,
        datefmt='%Y-%m-%d %H:%M:%S',
            handlers=[
            console_handler
        ])

    # Testing the method
    log("COMMAND_START", {"room_id": "test"})