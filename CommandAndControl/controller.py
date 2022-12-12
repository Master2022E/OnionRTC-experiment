#!/usr/bin/env python3
from fabric import Connection
from pyfiglet import figlet_format
from enum import Enum
from multiprocessing import Process
from starter import startSession
import time
class Client(Enum):
    c1 = "c1"
    c2 = "c2"
    c3 = "c3"
    c4 = "c4"
    c5 = "c5"
    c6 = "c6"
    d1 = "d1"
    d2 = "d2"
    d3 = "d3"
    d4 = "d4"
    d5 = "d5"
    d6 = "d6"

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

    name = str(client).split(".")[1]

    connection = getConnection(client)

    command = "./setup_fake_webcam.sh"

    print("Starting the client " + name + " with the command: " + command )
    with connection.cd("OnionRTC-experiment/client_scripts"):
        result = connection.run(command, hide=True)
        print(result)

def clientSession(client: Client) -> None:

    name = str(client).split(".")[1]

    connection = getConnection(client)

    command = "python3 OnionRTC.py " + name + " roomID1337 " + "10"

    print("Starting the client " + name + " with the command: " + command )
    with connection.cd("OnionRTC-experiment/Selenium"):
        result = connection.run(command, hide=False)
        print(result)

def runSession(alice: Client, bob: Client) -> None:
    '''
    Runs a session between two clients.

    The clients know what type of service it uses, if any.
    '''

    aliceWebcamProcess = Process(target=clientWebcam, args=(alice,))
    BobWebcamProcess = Process(target=clientWebcam, args=(bob,))

    print("Starting the webcams")
    aliceWebcamProcess.start()
    BobWebcamProcess.start()

    aliceSessionProcess = Process(target=clientSession, args=(alice,))
    BobSessionProcess = Process(target=clientSession, args=(bob,))
    
    print("Starting the session")
    aliceSessionProcess.start()
    BobSessionProcess.start()

    # Wait for the session processes to finish
    aliceSessionProcess.join()
    BobSessionProcess.join()

    # Kill the webcam processes
    aliceWebcamProcess.terminate()
    BobWebcamProcess.terminate()

    print("Session ended")


def main():

    print("Waiting to start a new session.")
    while(True):
        
        time.sleep(1)
        if(startSession()):
            print("Starting a new session")
            runSession(Client.c1, Client.d1)


# main method
if __name__ == "__main__":
    print(figlet_format("Command & Controller", font="slant"))
    main()
