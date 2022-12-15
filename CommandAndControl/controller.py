#!/usr/bin/env python3
import logging
import sys
import traceback
import uuid
from fabric import Connection
from pyfiglet import figlet_format
from enum import Enum
from multiprocessing import Process
from invoke import Responder, UnexpectedExit
from fabric import Connection
import os
from dotenv import load_dotenv
from starter import startSession
import time
import mongo
import custom_discord as discord
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

    aliceCleanUpProcess = Process(target=clientCleanup, args=(alice,),name=f'Clean-{str(alice).replace(" ", "")}')
    bobCleanUpProcess = Process(target=clientCleanup, args=(bob,),name=f'Clean-{str(bob).replace(" ", "")}')
    
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
    Same as cleanup(..) this could probably be done without spawning extra processes.
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
        logging.info("Killing the ffmpeg processes on " + name + " with the command: " + command )
        connection.run(command, hide=True)
        
    except(UnexpectedExit):
        pass

    logging.info("Target(s) neutralized")


def clientWebcam(client: Client) -> None:
    '''
    Takes a client and does the procedure for starting up a webcam on the client.
    This needs to run as a process, because we need to kill the process when we are done with the session.
    '''

    name = str(client)
    load_dotenv()

    passwd = os.environ.get("USER_SUDO_PASSWORD",None)
    if passwd == None:
        raise Exception("USER_SUDO_PASSWORD not set")

    
    
    connection = getConnection(client)
    with connection.cd("OnionRTC-experiment/client_scripts"):
        command = "./setup_fake_webcam_permissions.sh"
        logging.info("Configuring the client " + name + " webcam permissions with the command: " + command )
        try:
            sudopass = Responder(pattern=r'\[sudo\] password for agpbruger:', response=f'{passwd}\n')
            connection.run(command, hide=True, pty=True, watchers=[sudopass])
            logging.info(f"Webcam permissions on the client {name} configured")
        except(UnexpectedExit) as e:
            logging.info(f"Error command: {e.result.command} on {name} exited with {e.result.exited}")
            pass

        command = "./setup_fake_webcam.sh"
        logging.info("Starting the client " + name + " webcam")
        try:
            connection.run(command, hide=True)
        except(Exception) as e:
            pass
            
        # Run the script twice, because the first time it does sometime fail.. #hack
        try:
            connection.run(command, hide=True)
        except(Exception) as e:
            pass


def clientSession(client: Client, test_id: str, room_id: str) -> None:
    '''
    Takes a client and runs the OnionRTC.py script on the client.
    This needs to run as a process, so we can run multiple clients at the same time.
    '''

    name = str(client)

    connection = getConnection(client)
    timeout = 60
    command = f'python3 OnionRTC.py {name.replace(" ", "")} {test_id} {room_id} {timeout}'

    logging.info("Starting the client " + name + " with the command: " + command )
    mongo.log("COMMAND_SESSION_START", test_id=test_id, room_id=room_id, client_username=name.replace(" ", ""))
    with connection.cd("OnionRTC-experiment/Selenium"):
        try:
            connection.run(command, hide=True)
            logging.info(f"Session on the client {name} successfully ended")
        except(UnexpectedExit) as e:
            logging.error(f"Session failed on client {name}. Exited with {e.result.exited}")
            logging.error(f"command: {e.result.command}")
            logging.error(f"stdout:\n{e.result.stdout}")
            logging.error(f"stderr:\n{e.result.stderr}")
            discord.notify(header="Failed run!", message=f"Error in OnionRTC on client: {name}, Exit code: {e.result.exited}", errorMessage=f"Traceback: \n{e.result.stdout[max(-(len(e.result.stdout)),-1000):]}", test_id=test_id, room_id=room_id, client_id=name.replace(" ", ""))
            mongo.log("COMMAND_SESSION_FAILED", test_id=test_id, room_id=room_id, client_username=str(name).replace(" ", ""))
            return
    mongo.log("COMMAND_SESSION_SUCCESS", test_id=test_id, room_id=room_id, client_username=str(name).replace(" ", ""))



def runSession(alice: Client, bob: Client, test_id: str, room_id: str) -> None:
    '''
    Runs a session between two clients.

    The clients know what type of service it uses, if any.
    '''
    
    cleanup(alice, bob)

    aliceWebcamProcess = Process(target=clientWebcam, args=(alice,),name=f'Camera-{str(alice).replace(" ", "")}')
    bobWebcamProcess = Process(target=clientWebcam, args=(bob,),name=f'Camera-{str(bob).replace(" ", "")}')

    logging.info("Starting the webcams")
    aliceWebcamProcess.start()
    bobWebcamProcess.start()

    logging.info("Giving the webcams a head start")
    time.sleep(5)

    aliceSessionProcess = Process(target=clientSession, args=(alice, test_id, room_id),name=f'Session-{str(alice).replace(" ", "")}')
    bobSessionProcess = Process(target=clientSession, args=(bob, test_id, room_id),name=f'Session-{str(bob).replace(" ", "")}')
    
    logging.info("Starting the sessions")
    aliceSessionProcess.start()
    bobSessionProcess.start()

    # Wait for the session processes to finish
    aliceSessionProcess.join()
    bobSessionProcess.join()

    # Kill the webcam processes and wait for them to finish
    stop_webcam(aliceWebcamProcess, bobWebcamProcess)

    # Cleanup
    process_clean([aliceSessionProcess, bobSessionProcess, aliceWebcamProcess, bobWebcamProcess])
    cleanup(alice, bob)        

    logging.info("Session ended")

def main():

    testCases = [
        # One to one
        [Client.c1, Client.d1],

    ]

    testCases = [
        # One to one
        [Client.c1, Client.d1],
        [Client.c2, Client.d2],
        [Client.c3, Client.d3],
        [Client.c4, Client.d4],
        #[Client.c5, Client.d5], # I2P is not working
        [Client.c6, Client.d6],

        # Normal to Anonymized
        [Client.c1, Client.d2],
        [Client.c1, Client.d3],
        [Client.c1, Client.d4],
        #[Client.c1, Client.d5], # I2P is not working
        [Client.c1, Client.d6],

        # Tor to Tor
        [Client.c1, Client.d2],
        [Client.c2, Client.d3],
        [Client.c2, Client.d4],
        [Client.c3, Client.d4],
    ]
    test_id = str
    room_id = str
    
    logging.info("Waiting to start a new session.")
    while(True):
        try:
            if(startSession([0, 1, 0])):
                test_id = str(uuid.uuid4())
                mongo.log(loggingType="COMMAND_START_RUN", test_id=test_id)
                logging.info("Starting a new run, test_id: " + test_id)
                for testCase in testCases:
                    room_id = str(uuid.uuid4())
                    logging.info(f'Starting a test {test_id} in room {room_id} between [{str(testCase[0])}] and [{str(testCase[1])}]')
                    mongo.log(loggingType="COMMAND_START_TEST", test_id=test_id, room_id=room_id)
                    runSession(alice = testCase[0], bob = testCase[1], test_id=test_id, room_id=room_id)

                logging.info("Run completed, Waiting to start a new session")

            # NOTE: Makes sure that the application doesn't run too fast
            #       and that the application is closeable with CTRL+C.
            time.sleep(1) 
        except KeyboardInterrupt as e:
            raise(e)
        except Exception as e:
            # Get string of exception
            
            just_the_string = traceback.format_exc()
            logging.error(f"An error occurred: \nException: {e}\nTraceback: \n{just_the_string}")
            discord.notify(header="Crash!", message=f"Exception: {e}\nTraceback: \n{just_the_string}", test_id=test_id, room_id=room_id)
            pass


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

    logging.addLevelName( logging.WARNING, "\033[1;31m%s\033[1;0m" % logging.getLevelName(logging.WARNING))
    logging.addLevelName( logging.ERROR, "\033[1;41m%s\033[1;0m" % logging.getLevelName(logging.ERROR))

    discord.notify(header="Starting")
                
    print(figlet_format("Command & Controller", font="slant"))

    try:
        main()
    except KeyboardInterrupt:
        logging.info("Exiting the application")
        exit(0)
        