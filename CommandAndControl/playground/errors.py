#!/usr/bin/env python3
import logging
import sys
from fabric import Connection
from multiprocessing import Process
from invoke import UnexpectedExit
from fabric import Connection

class FabricException(Exception):
    pass

def getConnection() -> Connection:
    return Connection("agpbruger@c.thomsen-it.dk:22001")


def clientSession() -> None:


    connection = getConnection()
    command = f'python3 -c "raise Exception(\'This is a test\')"'
    logging.info("Starting the client with the command: " + command )


    with connection.cd("OnionRTC-experiment/Selenium"):
        try:
            result = connection.run(command, hide=True)
            # NOTE: The result is of this type:
            #       https://docs.pyinvoke.org/en/latest/api/runners.html#invoke.runners.Result
            
            logging.info(f"Session on the client successfully ended")
        except(UnexpectedExit) as e:
            result = e.result
            logging.error(f"Session on the client exited with {result.exited}")
            logging.error(f"command: {result.command}")
            logging.error(f"stdout:\n{result.stdout}")
            logging.error(f"stderr:\n{result.stderr}")
            logging.info(f"exception:\n{e}")



def runSession() -> None:
    '''
    Runs a session between two clients.

    The clients know what type of service it uses, if any.
    '''
    
    

def main():

    
    logging.info("Waiting to start a new session.")
    
    aliceSessionProcess = Process(target=clientSession, args=(),name=f'Session')
    
    logging.info("Starting the sessions")
    aliceSessionProcess.start()

    # Wait for the session processes to finish
    aliceSessionProcess.join()
    aliceSessionProcess.terminate()

    logging.info("Session ended")


# main method
if __name__ == "__main__":

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)


    logging.basicConfig(
        format=f'%(asctime)s %(levelname)-8s %(processName)-12s %(filename)s(%(lineno)d): %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S',
            handlers=[
            #logging.FileHandler("debug.log"),
            #logging.StreamHandler(), # Show everything on console
            console_handler # Only show INFO and above on console
        ])


    try:
        main()
    except KeyboardInterrupt as e:
        print("KeyboardInterrupt")