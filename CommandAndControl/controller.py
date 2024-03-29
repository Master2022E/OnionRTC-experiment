#!/usr/bin/env python3
import logging
import socket
import sys
import traceback
import uuid
from fabric import Connection
from pyfiglet import figlet_format
from enum import Enum
from multiprocessing import Process
from multiprocessing import Value
from invoke import Responder, UnexpectedExit,CommandTimedOut
from fabric import Connection
import os
from dotenv import load_dotenv
from starter import startSession
import time
import mongo
import custom_discord as discord
import os

def is_docker():
    path = '/proc/self/cgroup'
    return (
        os.path.exists('/.dockerenv') or
        os.path.isfile(path) and any('docker' in line for line in open(path))
    )


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

def kill_on_client(name, connection, command):
    try:
        connection.run(command, hide=True)
    except(UnexpectedExit) as e:
        # If the command fails, it is probably because there are no processes of that name running
        pass
    except socket.gaierror:
        logging.warning(f"Could not connect to " + name + " to run the command {command}, continuing anyway..")
    

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
    Takes a client and kills any processes that we might have started and should be running on the client.
    This could also have be done without spawning a process for running this function, since we exit at once.
    '''

    name = str(client)

    connection = getConnection(client)

    """
    # The commands to run on the client for cleanup
    "pkill -f "ffmpeg"" # Find and kill any ffmpeg processes
    "pkill -f geckodriver" # Find and kill any geckodriver processes
    "pkill -f firefox" # Find and kill any firefox processes
    'pkill -f "ssh -MfN -S /tmp/"' # Find and kill any ssh port forwarding processes
    'pkill -f "python3 OnionRTC.py"' # Find and kill any OnionRTC processes
    """

    commands = [
    'pkill -f "ffmpeg"',
    'pkill -f "geckodriver"',
    'pkill -f "firefox"',
    'pkill -f "ssh -MfN -S /tmp/"',
    'pkill -f "python3 OnionRTC.py"']
    
    logging.info("Killing the processes on " + name)
    for cmd in commands:
        kill_on_client(name, connection, cmd)
    logging.info(f"Target(s) neutralized, done cleaning up on {name}!")

    try:
        connection.close()
    except Exception as e:
        logging.error("Error while closing the connection to " + name + ": " + str(e))


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


def clientSession(client: Client, scenario_type: str, test_id: str, room_id: str,variable: Value) -> None:
    '''
    Takes a client and runs the OnionRTC.py script on the client.
    This needs to run as a process, so we can run multiple clients at the same time.

    variable is a multiprocessing.Value object, which is used to communicate with the main process about the result code.
    '''

    name = str(client)

    connection = getConnection(client)
    session_length = 60
    session_timeout = int(session_length*6)

    command = f'python3 OnionRTC.py {name.replace(" ", "")} {test_id} {room_id} {scenario_type} {session_length}'

    logging.info("Starting the client " + name + " with the command: " + command )
    with connection.cd("OnionRTC-experiment/Selenium"):
        try:
            connection.run(command, hide=True,timeout=session_timeout)
            logging.info(f"Session on the client {name} successfully ended")
            variable.value = 0
        except CommandTimedOut as e:
            logging.error(f"Session failed on client {name}. Timed out after {session_timeout} seconds")
            variable.value = 4
            discord.notify(header=f"Fabric run connection timed out",
             message=f"Session failed on client {name}. Timed out after {session_timeout} seconds",
              scenario_type=scenario_type, test_id=test_id, room_id=room_id, client_id=name.replace(" ", ""))
            return # From Error
        except(UnexpectedExit) as e:
            logging.error(f"Session failed on client {name}. Exited with {e.result.exited}")
            variable.value = e.result.exited
            
            if e.result.exited == 1:
                # Generic keyboard or Exception
                logging.error(f"command: {e.result.command}")
                logging.error(f"stdout:\n{e.result.stdout}")
                logging.error(f"stderr:\n{e.result.stderr}")
            
            elif e.result.exited == 2:
                # SSH connection error, after 3 retries
                # Could require a restart of the anonymization service on the client like Lokinet
                if client == Client.c6 or client == Client.d6:
                    # Policy: We restart the service and fail the session
                    passwd = os.environ.get("USER_SUDO_PASSWORD",None)
                    if passwd == None:
                        raise Exception("USER_SUDO_PASSWORD not set")                    
                    logging.error(f"Client {name} is having trouble connecting to the mongo server. Restarting the Lokinet service on the client")
                    command = f'sudo systemctl restart lokinet.service'
                    sudopass = Responder(pattern=r'\[sudo\] password for agpbruger:', response=f'{passwd}\n')
                    try:
                        connection.run(command, hide=True, pty=True, watchers=[sudopass])
                        logging.info(f"Lokinet service on the client {name} was successfully restarted")
                    except(UnexpectedExit) as e:
                        logging.error(f"Lokinet service on the client {name}. Exited with {e.result.exited} and error: \'{e.result.stdout}\'")       
                else:
                    logging.warning(f"No retry policy is defined for {name}!")
            elif e.result.exited == 3:
                # Anonymization service not running/ready, so we require a restart of the service
                # Could require a restart of the anonymization service on the client 

                # If Tor
                if client == Client.c2 or client == Client.d2 or \
                    client == Client.c3 or client == Client.d3 or \
                    client == Client.c4 or client == Client.d4:
                    # Policy: We restart the service and fail the session
                    passwd = os.environ.get("USER_SUDO_PASSWORD",None)
                    if passwd == None:
                        raise Exception("USER_SUDO_PASSWORD not set")                    
                    logging.error(f"Client {name} is having trouble connecting to the mongo server. Restarting the Tor service on the client")
                    command = f'sudo systemctl restart tor.service'
                    sudopass = Responder(pattern=r'\[sudo\] password for agpbruger:', response=f'{passwd}\n')
                    try:
                        connection.run(command, hide=True, pty=True, watchers=[sudopass])
                        logging.info(f"Tor service on the client {name} was successfully restarted")
                    except(UnexpectedExit) as e:
                        logging.error(f"Tor service on the client {name}. Exited with {e.result.exited} and error: \'{e.result.stdout}\'")

                # If I2p
                #elif client == Client.c5 or client == Client.d5:
                # FIXME: Implement I2p restart policy and service check.

                # If Lokinet
                elif client == Client.c6 or client == Client.d6:
                    # Policy: We restart the service and fail the session
                    passwd = os.environ.get("USER_SUDO_PASSWORD",None)
                    if passwd == None:
                        raise Exception("USER_SUDO_PASSWORD not set")                    
                    logging.error(f"Client {name} is having trouble connecting to the mongo server. Restarting the Lokinet service on the client")
                    command = f'sudo systemctl restart lokinet.service'
                    sudopass = Responder(pattern=r'\[sudo\] password for agpbruger:', response=f'{passwd}\n')
                    try:
                        connection.run(command, hide=True, pty=True, watchers=[sudopass])
                        logging.info(f"Lokinet service on the client {name} was successfully restarted")
                        discord.notify(header=f"Lokinet service on the client {name} was successfully restarted",
                         scenario_type=scenario_type, test_id=test_id, room_id=room_id, client_id=name.replace(" ", ""))
                    except(UnexpectedExit) as e:
                        logging.error(f"Lokinet service on the client {name}. Exited with {e.result.exited} and error: \'{e.result.stdout}\'")   
                        discord.notify(header=f"Lokinet service on the client {name} was not restarted",
                         message=f"Lokinet service on the client {name}. Exited with {e.result.exited} and error: \'{e.result.stdout}\'",
                          scenario_type=scenario_type, test_id=test_id, room_id=room_id, client_id=name.replace(" ", ""))
                else:
                    logging.warning(f"No retry policy is defined for {name}!")
                    discord.notify(header=f"No retry policy is defined for {name}",
                     message=f"Lokinet service on the client {name}. Exited with {e.result.exited} and error: \'{e.result.stdout}\'",
                      scenario_type=scenario_type, test_id=test_id, room_id=room_id, client_id=name.replace(" ", ""))
            elif e.result.exited == 5:
                # The "TimeoutException" was raised and exit code was 5
                # It means that the http call for the WebRTC page took too long to finish.
                # One retry was done, but it failed.
                # So the session failed while setting up the session!
                discord.notify(header=f"The HTTP call took too long to finish: {scenario_type}",
                 message=f"Nothing to do, just a notification",
                  errorMessage=f"Traceback: \n{e.result.stdout[max(-(len(e.result.stdout)),-1000):]}",
                   scenario_type=scenario_type, test_id=test_id, room_id=room_id, client_id=name.replace(" ", ""))                
            
            else:
                exception_str = e.result.stdout.split(", exception=")[1].split(") \n")[0]
                logging.warning(f'No retry policy is defined for exit-code: \'{e.result.exited}\'! Exception was: {exception_str}')
                discord.notify(header=f"No retry policy is defined for exit-code",
                 message=f'No retry policy is defined for exit-code: \'{e.result.exited}\'! Exception was: {exception_str}',
                  scenario_type=scenario_type, test_id=test_id, room_id=room_id, client_id=name.replace(" ", ""))
                
            discord.notify(header=f"Failed run! Scenario: {scenario_type}",
             message=f"Error in OnionRTC on client: {name}, Exit code: {e.result.exited}",
              errorMessage=f"Traceback: \n{e.result.stdout[max(-(len(e.result.stdout)),-1000):]}",
               scenario_type=scenario_type, test_id=test_id, room_id=room_id, client_id=name.replace(" ", ""))

            #mongo.log("COMMAND_SESSION_FAILED", scenario_type=scenario_type, test_id=test_id, room_id=room_id, client_username=str(name).replace(" ", ""))
            return # From Error

    #mongo.log("COMMAND_SESSION_SUCCESS", scenario_type=scenario_type, test_id=test_id, room_id=room_id, client_username=str(name).replace(" ", ""))
    return # From Success
    
def classify_session(alice, bob, scenario_type, test_id, room_id):
    '''
    Classifies the session based on the shared variable.
    '''


    if alice.return_code == 0 and bob.return_code == 0:
        mongo.log("COMMAND_SESSION_SUCCESS", scenario_type=scenario_type, test_id=test_id, room_id=room_id)
    elif alice.return_code == 5 or bob.return_code == 5:
        mongo.log("COMMAND_SESSION_FAILED_SETUP", scenario_type=scenario_type, test_id=test_id, room_id=room_id)
    else:
        mongo.log("COMMAND_SESSION_FAILED", scenario_type=scenario_type, test_id=test_id, room_id=room_id)
        
        

def runSession(alice: Client, bob: Client, scenario_type: str, test_id: str, room_id: str) -> None:
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

    # create shared variable
    alice_variable = Value('f', -1)
    bob_variable = Value('f', -1)

    aliceSessionProcess = Process(target=clientSession, args=(alice, scenario_type, test_id, room_id,alice_variable,),name=f'Session-{str(alice).replace(" ", "")}')
    bobSessionProcess = Process(target=clientSession, args=(bob, scenario_type, test_id, room_id,bob_variable,),name=f'Session-{str(bob).replace(" ", "")}')
    
    
    run_session(scenario_type, test_id, room_id, aliceSessionProcess, bobSessionProcess)

    # Give client object the return code
    alice.return_code = alice_variable.value
    bob.return_code = bob_variable.value

    # Classify the session based on their exit codes
    classify_session(alice, bob, scenario_type, test_id, room_id)

    # Kill the webcam processes and wait for them to finish
    stop_webcam(aliceWebcamProcess, bobWebcamProcess)

    # Cleanup
    process_clean([aliceSessionProcess, bobSessionProcess, aliceWebcamProcess, bobWebcamProcess])
    cleanup(alice, bob)        

    logging.info("Session ended\n\n")

def run_session(scenario_type, test_id, room_id, aliceSessionProcess, bobSessionProcess):
    '''
    Runs the session processes and waits for them to finish.
    '''

    logging.info("Starting the sessions")
    mongo.log("COMMAND_SESSION_START", scenario_type=scenario_type, test_id=test_id, room_id=room_id)
    aliceSessionProcess.start()
    bobSessionProcess.start()

    # Wait for the session processes to finish
    aliceSessionProcess.join()
    bobSessionProcess.join()
    

def main():

    testCases = [
        # One to one
        {"clientC": Client.c1, "clientD": Client.d1, "type": "1"},

    ]

    testCases = [
        # One to one
        {"clientC": Client.c1, "clientD": Client.d1, "type": "1"},
        {"clientC": Client.c2, "clientD": Client.d2, "type": "2"},
        {"clientC": Client.c3, "clientD": Client.d3, "type": "3"},
        {"clientC": Client.c4, "clientD": Client.d4, "type": "4"},
        {"clientC": Client.c6, "clientD": Client.d6, "type": "5"},

        # Normal to Anonymized
        {"clientC": Client.c1, "clientD": Client.d2, "type": "6"},
        {"clientC": Client.c2, "clientD": Client.d1, "type": "7"},

        {"clientC": Client.c1, "clientD": Client.d3, "type": "8"},
        {"clientC": Client.c3, "clientD": Client.d1, "type": "9"},

        {"clientC": Client.c1, "clientD": Client.d4, "type": "10"},
        {"clientC": Client.c4, "clientD": Client.d1, "type": "11"},


        {"clientC": Client.c1, "clientD": Client.d6, "type": "12"},
        {"clientC": Client.c6, "clientD": Client.d1, "type": "13"},

        # Tor to Tor
        {"clientC": Client.c2, "clientD": Client.d3, "type": "14"},
        {"clientC": Client.c3, "clientD": Client.d2, "type": "15"},

        {"clientC": Client.c2, "clientD": Client.d4, "type": "16"},
        {"clientC": Client.c4, "clientD": Client.d2, "type": "17"},

        {"clientC": Client.c3, "clientD": Client.d4, "type": "18"},
        {"clientC": Client.c4, "clientD": Client.d3, "type": "19"},


    ]

    test_id = str
    room_id = str
    
    logging.info("Waiting to start a new session.")
    while(True):
        try:
            if(startSession([0, 0, 1])): # Set to one second, so we run as fast a possible.
                test_id = str(uuid.uuid4())
                mongo.log(loggingType="COMMAND_START_RUN", test_id=test_id)
                logging.info("Starting a new run, test_id: " + test_id)
                for index,testCase in enumerate(testCases):
                    room_id = str(uuid.uuid4())
                    logging.info(f'Starting scenario: [{testCase["type"]}] [{index+1} of {len(testCases)} cases] between [{testCase["clientC"]}] and [{testCase["clientD"]}] in room: {room_id} with test id: {test_id}')
                    mongo.log(loggingType="COMMAND_START_TEST", scenario_type=testCase["type"], test_id=test_id, room_id=room_id)
                    runSession(alice =testCase["clientC"], bob = testCase["clientD"], scenario_type=testCase["type"], test_id=test_id, room_id=room_id)

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


# main method
if __name__ == "__main__":

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)


    logging.basicConfig(
        format=f'%(asctime)s %(levelname)s %(processName)-12s %(filename)s(%(lineno)d): %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S',
            handlers=[
            logging.FileHandler("log/debug.log"),
            #logging.StreamHandler(), # Show everything on console
            console_handler # Only show INFO and above on console
        ])

    logging.addLevelName( logging.WARNING, "\033[1;31m%s\033[1;0m" % logging.getLevelName(logging.WARNING))
    logging.addLevelName( logging.ERROR, "\033[1;41m%s\033[1;0m" % logging.getLevelName(logging.ERROR))
    discord.notify(header="Starting",message=f'Running from docker container: {is_docker()}')
                
    print(figlet_format("Command & Controller", font="slant"))

    try:
        main()
    except KeyboardInterrupt:
        logging.info("Exiting the application")
        discord.notify(header="Turning off", message=f"Caused by a keyboard interrupt!")
        exit(0)
        