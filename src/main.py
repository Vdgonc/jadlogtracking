import logging
from bot import Bot
from sys import exit
from os import environ

logging.basicConfig(level=environ.get("LOGLEVEL", "INFO"), format="%(asctime)s - %(levelname)s - %(message)s")

TRACKID = environ.get("TRACKID")
TOKEN = environ.get("TOKEN")
CHATID = environ.get("CHATID")
STATUSDIR = environ.get("STATUSDIR", "./data/status.json")

if __name__ == "__main__":
    if TRACKID is None or TOKEN is None or CHATID is None:
        logging.error(f'Error on load env vars: [TRACKID {TRACKID} - TOKEN {TOKEN} - CHATID {CHATID}]')
        exit(1)

    bot = Bot(trackid=TRACKID, telegramToken=TOKEN)

    bot.compare(statusfile=STATUSDIR, chatID=CHATID)


