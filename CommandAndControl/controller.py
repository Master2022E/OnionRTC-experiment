#!/usr/bin/env python3
from fabric import Connection, SerialGroup
from pyfiglet import figlet_format


def main():
    connections= {}
    connections["c1"] = Connection("agpbruger@c.thomsen-it.dk:22001")
    connections["c2"] = Connection("agpbruger@c.thomsen-it.dk:22002")
    connections["c3"] = Connection("agpbruger@c.thomsen-it.dk:22003")
    connections["c4"] = Connection("agpbruger@c.thomsen-it.dk:22004")
    connections["c5"] = Connection("agpbruger@c.thomsen-it.dk:22005")
    connections["c6"] = Connection("agpbruger@10.3.0.6:22022", gateway=Connection('agpbruger@c.thomsen-it.dk:22022'))
    connections["d1"] = Connection("agpbruger@d.thomsen-it.dk:22001")
    connections["d2"] = Connection("agpbruger@d.thomsen-it.dk:22002")
    connections["d3"] = Connection("agpbruger@d.thomsen-it.dk:22003")
    connections["d4"] = Connection("agpbruger@d.thomsen-it.dk:22004")
    connections["d5"] = Connection("agpbruger@d.thomsen-it.dk:22005")
    connections["d6"] = Connection("agpbruger@10.4.0.6:22022", gateway=Connection('agpbruger@d.thomsen-it.dk:22022'))



    group = SerialGroup.from_connections([*connections.values()])

    try:
        results = group.run('hostname',hide=True)
        for connection, result in results.items():
            print("{0.host}:{1.port}: {2.stdout}".format(connection,connection, result))

    except Exception as e:
        print("Error: {0}".format(e))

# main method
if __name__ == "__main__":
    print(figlet_format("Command & Controller", font="slant"))
    main()
