#!/usr/bin/python3
from ssh_pymongo import MongoSession
from sshtunnel import SSHTunnelForwarder
from pymongo import MongoClient
import os
from dotenv import load_dotenv
import json
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
        return subprocess.check_call(['ssh', '-S', self.socket, '-O', cmd, '-l', self.user, self.host])

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, type, value, traceback):
        self.stop()


load_dotenv()
print(os.getenv('MONGO_HOST'))

my_local_port = random.randint(10000, 65535)

with SSHTunnel(os.getenv("MONGO_HOST"), os.getenv("SSH_TUNNEL_USER"), os.getenv("SSH_TUNNEL_PORT"), os.getenv("SSH_KEY_PATH"), os.getenv("MONGO_PORT"),my_local_port) as tunnel:
    print("Connected on port {} at {}".format(tunnel.local_port, tunnel.local_host))
    address = f'mongodb://{os.getenv("MONGO_USER")}:{os.getenv("MONGO_PASSWORD")}@127.0.0.1:{my_local_port}'
    client = MongoClient(address)
    database= client["observertc-reports"]

    # the collection we want to query
    reportsDatabase = database.calls
    print(reportsDatabase)
    print(database.reports)
    
    data = {"test":f"ssh_tunnel "}
    data['timestamp'] = str(datetime.now())

    try:
        reportsDatabase.insert_one(data)
        print("Done sending: {}".format(data))
    except (KeyboardInterrupt, Exception) as e:
        print("Error: ", e)

    