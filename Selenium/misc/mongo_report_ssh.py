#!/usr/bin/python3
from pymongo import MongoClient
import os
from dotenv import load_dotenv
from datetime import datetime
import time
import subprocess
import random
import tempfile


# taken from https://stackoverflow.com/questions/4364355/how-to-open-an-ssh-tunnel-using-python
class SSHTunnel:

    def __init__(self, host, user, port, key, remote_port,local_port):
        self.host = host
        self.user = user
        self.port = port
        self.key = key
        self.remote_port = remote_port
        # Get a temporary file name
        tmpfile = tempfile.NamedTemporaryFile()
        tmpfile.close()
        self.socket = tmpfile.name
        self.local_port = local_port
        self.local_host = '127.0.0.1'
        self.open = False

    def start(self):
        exit_status = subprocess.call(['ssh', '-MfN',
            '-S', self.socket,
            '-i', self.key,
            '-l', self.user,
            '-L', '{}:{}:{}'.format(self.local_port, self.local_host, self.remote_port),
            '-o', 'ExitOnForwardFailure=True',
            self.host,
            '-p', '22022'
        ])
        if exit_status != 0:
            raise Exception('SSH tunnel failed with status: {}'.format(exit_status))
        if self.send_control_command('check') != 0:
            raise Exception('SSH tunnel failed to check')
        self.open = True

    def stop(self):
        if self.open:
            if self.send_control_command('exit') != 0:
                raise Exception('SSH tunnel failed to exit')
            self.open = False

    def send_control_command(self, cmd):
        return subprocess.check_call(['ssh', '-S', self.socket, '-O', cmd, '-l', self.user, self.host], 
        stderr=subprocess.PIPE) # Add stderr=subprocess.PIPE to suppress output from start() and stop()

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, type, value, traceback):
        self.stop()

mongo_conn = None
ssh_conn = None
logging_global = print


logging_str = ["NOT_SET","CLIENT_START","CLIENT_RUNNING", "CLIENT_END", "CLIENT_ERROR"]
logging_types = dict()
for type in logging_str:
    logging_types[type] = type

"""
This function uses a SSH tunnel to connect to a remote MongoDB instance.
"""
def setup_mongo_connection(logging=None):
    global logging_global
    global ssh_conn

    if logging is not None:
        logging_global = logging.info
    else:
        logging_global = print
    
    load_dotenv()

    my_local_port = random.randint(10000, 65535)

    conn = SSHTunnel(os.getenv("MONGO_HOST"), os.getenv("SSH_TUNNEL_USER"), os.getenv("SSH_TUNNEL_PORT"), os.getenv("SSH_KEY_PATH"), os.getenv("MONGO_PORT"),my_local_port)
    conn.start()
    ssh_conn = conn

    #logging_global("Connected on port {} at {}".format(conn.local_port, conn.local_host))
    address = f'mongodb://{os.getenv("MONGO_USER")}:{os.getenv("MONGO_PASSWORD")}@127.0.0.1:{my_local_port}'
    client = MongoClient(address)

    return client

def close_mongo_connection():
    global mongo_conn
    global ssh_conn

    if mongo_conn is not None:
        try:
            mongo_conn.close()
            mongo_conn = None
        except Exception as e:
            pass
    if ssh_conn is not None:
        try:
            ssh_conn.stop()
            ssh_conn = None
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