#! /usr/bin/env python3
"""
    @Author: Thorsten liepert <thorsten@liepert.dev>
    @Date: 06.09.2024
    @CLicense: MIT
    @Description: A Discord bot that will handle log files generated by a SCUM server
                  and will send various events to discord.
"""
# pylint: disable=global-statement, too-many-branches, too-many-lines, import-error
import os
import threading
import socketserver

from dotenv import load_dotenv

import discord_client
from modules.webui import MyHttpRequestHandler

load_dotenv()
LOG_CHECK_INTERVAL = os.getenv("LOG_CHECK_INTERVAL")

if LOG_CHECK_INTERVAL is None:
    LOG_CHECK_INTERVAL = 60.0
else:
    LOG_CHECK_INTERVAL = float(LOG_CHECK_INTERVAL)

HELP_COMMAND = os.getenv("BOT_HELP_COMMAND")
if HELP_COMMAND is None:
    HELP_COMMAND = "buffi"


WEAPON_LOOKUP = {
    "Compound_Bow_C": "compund bow"
}

MAX_MESSAGE_LENGTH = 1000

def run_client():
    """ run client """
    # client.run(config.token)
    discord_client.run_client()

def web_thread() -> None:
    """ threads """
    # Create an object of the above class
    handler_object = MyHttpRequestHandler

    port = 8000
    my_server = socketserver.TCPServer(("", port), handler_object)

    # Star the server
    my_server.serve_forever()
    # while True:
    #     time.sleep(5)
    #     print("Thread 2 is alive!")


t1 = threading.Thread(target=run_client, name="Discord Bot")
t2 = threading.Thread(target=web_thread, name="Web UI")


def main():
    """ main """
    try:
        t1.start()
        t2.start()
    finally:
        t1.join()
        t2.join()

if __name__=='__main__':
    main()
