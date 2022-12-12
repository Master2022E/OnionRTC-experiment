#!/usr/bin/env python3
import logging
import sys
from fabric import Connection
from pyfiglet import figlet_format
from enum import Enum
from multiprocessing import Process
from starter import startSession
import time
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

def clientWebcam(client: Client) -> None:

    name = str(client)

    connection = getConnection(client)

    command = "./setup_fake_webcam.sh"

    logging.info("Starting the client " + name + " with the command: " + command )
    with connection.cd("OnionRTC-experiment/client_scripts"):
        result = connection.run(command, hide=True)
        logging.info(result)

def clientSession(client: Client) -> None:

    name = str(client)

    connection = getConnection(client)

    command = "python3 OnionRTC.py " + name.replace(" ", "") + " roomID1337 " + "10"

    logging.info("Starting the client " + name + " with the command: " + command )
    with connection.cd("OnionRTC-experiment/Selenium"):
        result = connection.run(command, hide=False)
        logging.info(result)

def runSession(alice: Client, bob: Client) -> None:
    '''
    Runs a session between two clients.

    The clients know what type of service it uses, if any.
    '''

    aliceWebcamProcess = Process(target=clientWebcam, args=(alice,))
    BobWebcamProcess = Process(target=clientWebcam, args=(bob,))

    logging.info("Starting the webcams")
    aliceWebcamProcess.start()
    BobWebcamProcess.start()

    aliceSessionProcess = Process(target=clientSession, args=(alice,))
    BobSessionProcess = Process(target=clientSession, args=(bob,))
    
    logging.info("Starting the session")
    aliceSessionProcess.start()
    BobSessionProcess.start()

    # Wait for the session processes to finish
    aliceSessionProcess.join()
    BobSessionProcess.join()

    # Kill the webcam processes
    aliceWebcamProcess.terminate()
    BobWebcamProcess.terminate()

    logging.info("Session ended")


def main():

    testCases = [
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
        if(startSession()):
            logging.info("Starting a new run.")
            for testCase in testCases:
                logging.info(f'Starting a session between [{str(testCase[0])}] and [{str(testCase[1])}]')
                #runSession(testCase[0], testCase[1])
                #runSession(Client.c1, Client.d1)

            logging.info("Run completed.")

        # NOTE: Makes sure that the application doesn't run too fast
        #       and that the application is closeable with CTRL+C.
        time.sleep(1) 


# main method
if __name__ == "__main__":

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)

    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S',
            handlers=[
            logging.FileHandler("debug.log"),
            #logging.StreamHandler(), # Show everything on console
            console_handler # Only show INFO and above on console
        ])
                
    print(figlet_format("Command & Controller", font="slant"))
    main()
