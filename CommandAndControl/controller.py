#!/usr/bin/env python3
import logging
import sys
import uuid
from fabric import Connection
from pyfiglet import figlet_format
from enum import Enum
from multiprocessing import Process
from invoke import Responder
from fabric import Connection
import os
from dotenv import load_dotenv
from starter import startSession
import time
import mongo
class Client(Enum):
    c1 = "c1 - Normal"
    c2 = "c2 - Tor Normal"
    c3 = "c3 - Tor Europe"
    c4 = "c4 - Tor Scandinavia"
    c5 = "c5 - I2P"
    c6 = "c6 - Lokinet"
    d1 = "d1 - Normal"
    d2 = "d2 - Tor Normal"
    d3 = "d3 - Tor Europe"
    d4 = "d4 - Tor Scandinavia"
    d5 = "d5 - I2P"
    d6 = "d6 - Lokinet"

    def __str__(self) -> str:
        return self.value

def getConnection(c: Client) -> Connection:
    if c == Client.c1:
        return Connection("agpbruger@c.thomsen-it.dk:22001")
    if c == Client.c2:
        return Connection("agpbruger@c.thomsen-it.dk:22002")
    if c == Client.c3:
        return Connection("agpbruger@c.thomsen-it.dk:22003")
    if c == Client.c4:
        return Connection("agpbruger@c.thomsen-it.dk:22004")
    if c == Client.c5:
        return Connection("agpbruger@c.thomsen-it.dk:22005")
    if c == Client.c6:
        return Connection("agpbruger@10.3.0.6:22022", gateway=Connection('agpbruger@c.thomsen-it.dk:22022'))
    if c == Client.d1:
        return Connection("agpbruger@d.thomsen-it.dk:22001")
    if c == Client.d2:
        return Connection("agpbruger@d.thomsen-it.dk:22002")
    if c == Client.d3:
        return Connection("agpbruger@d.thomsen-it.dk:22003")
    if c == Client.d4:
        return Connection("agpbruger@d.thomsen-it.dk:22004")
    if c == Client.d5:
        return Connection("agpbruger@d.thomsen-it.dk:22005")
    if c == Client.d6:
        return Connection("agpbruger@10.4.0.6:22022", gateway=Connection('agpbruger@d.thomsen-it.dk:22022'))
    
    return None 

def process_clean(processes: list[Process]) -> None:
    '''
    Takes a list of processes and calls close() on them
    '''

    # Cleanup the process objects
    for proces in processes:
        proces.close()

def cleanup(alice: Client, bob: Client):
    '''
    Takes two clients and call the clientCleanup function.
    This could propably be done without spawning extra processes,
    but now we are using the "name" parameter to name the processes,
    which makes it easier to follow which client is doing what.
    '''

    aliceCleanUpProcess = Process(target=clientCleanup, args=(alice,),name=f'{str(alice).replace(" ", "")}')
    bobCleanUpProcess = Process(target=clientCleanup, args=(bob,),name=f'{str(bob).replace(" ", "")}')
    
    logging.info("Cleaning up")
    try:
        aliceCleanUpProcess.start()
        bobCleanUpProcess.start()
        aliceCleanUpProcess.join()
        bobCleanUpProcess.join()
    except Exception as e:
        logging.error("Error while cleaning up: " + str(e))
        


def stop_webcam(aliceWebcamProcess: Process, bobWebcamProcess: Process):
    '''
    Takes two webcam processes, kills them and waits for them to finish.
    Same as cleanup(..) this could propably be done without spawning extra processes.
    '''

    aliceWebcamProcess.kill()
    bobWebcamProcess.kill()
    
    aliceWebcamProcess.join()
    bobWebcamProcess.join()

def clientCleanup(client: Client) -> None:
    '''
    Takes a client and kills any ffmpeg processes that might be running on the client.
    This could also have be done without spawning a process, since we exit at once.
    '''

    name = str(client)

    connection = getConnection(client)

    # Find and kill any ffmpeg processes
    command = "kill $(ps aux | grep '[f]fmpeg' | awk '{print $2}')"
    try:
        with connection as conn:
            logging.info("Cleaning the client " + name + " with the command: " + command )
            result = conn.run(command, hide=True)
            #logging.info(result)
    except:
        pass

def clientWebcam(client: Client) -> None:
    '''
    Takes a client and does the procedure for starting up a webcam on the client.
    This needs to run as a process, because we need to kill the process when we are done with the session.
    '''

    name = str(client)

    connection = getConnection(client)
    load_dotenv()

    passwd = os.environ.get("USER_SUDO_PASSWORD",None)
    if passwd == None:
        raise Exception("USER_SUDO_PASSWORD not set")

    # Handle root password for running commands that require sudo
    sudopass = Responder(pattern=r'\[sudo\] password for agpbruger:', response=f'{passwd}\n')
    command = "./setup_fake_webcam_permissions.sh"

    logging.info("Configuring the client " + name + " webcam with the command: " + command )
    with connection.cd("OnionRTC-experiment/client_scripts"):
        result = connection.run(command, hide=True, pty=True, watchers=[sudopass])
        #logging.info(result)


    command = "./setup_fake_webcam.sh"

    logging.info("Starting the client " + name + " webcam with the command: " + command )
    with connection.cd("OnionRTC-experiment/client_scripts"):
        result = connection.run(command, hide=True)
        logging.info(result)

def clientSession(client: Client, test_id: str, room_id: str) -> None:
    '''
    Takes a client and runs the OnionRTC.py script on the client.
    This needs to run as a process, so we can run multiple clients at the same time.
    '''

    name = str(client)

    connection = getConnection(client)
    timeout = 10
    command = f'python3 OnionRTC.py {name.replace(" ", "")} {test_id} {room_id} {timeout}'

    logging.info("Starting the client " + name + " with the command: " + command )
    mongo.log("COMMAND_START", test_id=test_id, room_id=room_id, client_username=name.replace(" ", ""))
    with connection.cd("OnionRTC-experiment/Selenium"):
        result = connection.run(command, hide=False)
        logging.info(result)
    mongo.log("COMMAND_END", test_id=test_id, room_id=room_id, client_username=str(name).replace(" ", ""))



def runSession(alice: Client, bob: Client, test_id: str, room_id: str) -> None:
    '''
    Runs a session between two clients.

    The clients know what type of service it uses, if any.
    '''
    
    cleanup(alice, bob)

    aliceWebcamProcess = Process(target=clientWebcam, args=(alice,),name=f'{str(alice).replace(" ", "")}')
    bobWebcamProcess = Process(target=clientWebcam, args=(bob,),name=f'{str(bob).replace(" ", "")}')

    logging.info("Starting the webcams")
    aliceWebcamProcess.start()
    bobWebcamProcess.start()

    aliceSessionProcess = Process(target=clientSession, args=(alice, test_id, room_id))
    bobSessionProcess = Process(target=clientSession, args=(bob, test_id, room_id))
    
    logging.info("Starting the session")
    aliceSessionProcess.start()
    bobSessionProcess.start()

    # Wait for the session processes to finish
    aliceSessionProcess.join()
    bobSessionProcess.join()

    # Kill the webcam processes and wait for them to finish
    stop_webcam(aliceWebcamProcess, bobWebcamProcess)

    # Cleanup
    process_clean([aliceSessionProcess, bobSessionProcess,aliceWebcamProcess,bobWebcamProcess])
    cleanup(alice, bob)        

    logging.info("Session ended")

def main():

    testCases = [
        # One to one
        [Client.c1, Client.d1],

    ]

    testCases_All = [
        # One to one
        [Client.c1, Client.d1],
        [Client.c2, Client.d2],
        [Client.c3, Client.d3],
        [Client.c4, Client.d4],
        [Client.c5, Client.d5],
        [Client.c6, Client.d6],

        # Normal to Anonymized
        [Client.c1, Client.d2],
        [Client.c1, Client.d3],
        [Client.c1, Client.d4],
        [Client.c1, Client.d5],
        [Client.c1, Client.d6],

        # Tor to Tor
        [Client.c1, Client.d2],
        [Client.c2, Client.d3],
        [Client.c2, Client.d4],
        [Client.c3, Client.d4],
    ]
    
    logging.info("Waiting to start a new session.")
    while(True):
        if(startSession([0, 1, 0])):
            test_id = str(uuid.uuid4())
            mongo.log(loggingType="COMMAND_START_RUN", test_id=test_id)
            logging.info("Starting a new run, test_id: " + test_id)
            for testCase in testCases:
                room_id = str(uuid.uuid4())
                logging.info(f'Starting a test {test_id} in room {room_id} between [{str(testCase[0])}] and [{str(testCase[1])}]')
                mongo.log(loggingType="COMMAND_START_TEST", test_id=test_id, room_id=room_id)
                runSession(alice = testCase[0], bob = testCase[1], test_id=test_id, room_id=room_id)

            logging.info("Run completed.")

        # NOTE: Makes sure that the application doesn't run too fast
        #       and that the application is closeable with CTRL+C.
        time.sleep(1) 



# main method
if __name__ == "__main__":

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)


    logging.basicConfig(
        format=f'%(asctime)s %(levelname)s %(processName)-12s %(filename)s(%(lineno)d): %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S',
            handlers=[
            logging.FileHandler("debug.log"),
            #logging.StreamHandler(), # Show everything on console
            console_handler # Only show INFO and above on console
        ])



                
    print(figlet_format("Command & Controller", font="slant"))
    try:
        main()
    except KeyboardInterrupt as e:
        print("KeyboardInterrupt")