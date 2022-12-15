#!/usr/bin/env python3

import logging
import sys
from dotenv import load_dotenv
import os
from discord_webhook import DiscordWebhook
import json

"""

The discord module is used to send notifications to a discord webhook.

To test the printing in discord, run this file directly.

"""


def notify(header: str = None, message: str = "", errorMessage: str = "" , test_id = None, room_id = None, client_id = None, dict = None):
    """
    Sends a notification to the discord webhook

    The header will be shown first in bold.

    The optional Parameters will be shown in a code block.

    The dict will be shown in a code block with nice format.

    Parameters
    ----------
    message : str
        The message to be sent
    header : str, optional
        The header of the message, by default None
    test_id : str, optional
        The test id, by default None
    room_id : str, optional
        The room id, by default None
    client_id : str, optional
        The client id, by default None
    client_username : str, optional 
        The client username, by default None
    """

    load_dotenv()

    discordHook = os.getenv("DISCORD_HOOK")

    if(discordHook is None):
        logging.info("Discord webhook not configured. To send notifications, add the webhook to the environment variable DISCORD_HOOK")
        return

    if(header is not None):
        header = f"**{header}**\n"

    basicInfo = ""
    if(test_id is not None or room_id is not None or client_id is not None):
        basicInfo = "\n```shell\n"
        if(test_id is not None):
            basicInfo += f"Test ID: {test_id}\n"
        if(room_id is not None):
            basicInfo += f"Room ID: {room_id}\n"
        if(client_id is not None):
            basicInfo += f"Client ID: {client_id}\n"
        basicInfo += "```\n"

    dictText = ""
    if(dict is not None):
        dictText = "```json\n"
        dictText += json.dumps(dict, indent=4)
        dictText += "\n```"
    
    message = f"{header}{message}{basicInfo}{errorMessage}{dictText}"

    webhook = DiscordWebhook(url=discordHook, content=message)
    response = webhook.execute()
    if(response.status_code != 200):
        logging.error(f"Discord webhook failed with status code {response.status_code}")
        logging.info(response.text)
    else:
        logging.info("Discord webhook sent successfully")


if __name__ == "__main__":
        # Setup logging
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging.DEBUG,
        datefmt='%Y-%m-%d %H:%M:%S',
            handlers=[
            console_handler
        ])
        
    #notify("Testcase 1")
    #notify("Testcase 2", test_id="test_id")
    #notify("Testcase 3", test_id="test_id", room_id="room_id")
    #notify("Testcase 4", test_id="test_id", room_id="room_id",client_id="client_id")
    #notify("Testcase 5", test_id="test_id", room_id="room_id",client_id="client_id", dict={"test": "test", "test1": {"test2": "test2"}, "test3": [123, 321]})
    #notify("Testcase 6", dict={"test": "test", "test1": {"test2": "test2"}, "test3": [123, 321]})
    #notify("Testcase 7", header="Error")

    notify(header="Testcase 4", message="message here :)", errorMessage="Stack trace", test_id="test_id", room_id="room_id",client_id="client_id")
