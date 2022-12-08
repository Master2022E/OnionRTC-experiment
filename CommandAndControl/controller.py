#!/usr/bin/env python3
from fabric import Connection, SerialGroup
from pyfiglet import figlet_format
from enum import Enum


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

def main():
   

    group = SerialGroup.from_connections([getConnection(Client.c1),
                                          getConnection(Client.c2),
                                          getConnection(Client.c3),
                                          getConnection(Client.c4),
                                          getConnection(Client.c5),
                                          getConnection(Client.c6),
                                          getConnection(Client.d1),
                                          getConnection(Client.d2),
                                          getConnection(Client.d3),
                                          getConnection(Client.d4),
                                          getConnection(Client.d5),
                                          getConnection(Client.d6)])

    try:
        results = group.run('hostname',hide=True)
        for connection, result in results.items():
            print("{0.host}:{1.port}: {2.stdout}".format(connection,connection, result))

    except Exception as e:
        print("Error: {0}".format(e))

    # Test that all connections are working.
    #for connection in connections.values():
    #    print("{0}:{1}: {2}".format(connection.host ,connection.port, str(connection.is_connected)))

# main method
if __name__ == "__main__":
    print(figlet_format("Command & Controller", font="slant"))
    main()
