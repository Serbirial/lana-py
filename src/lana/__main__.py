import json
import logging
import os
import threading
import time

import requests

from lana.api import main as api_main
from lana.args_util import parse_args
from lana.bot import LanaAR
from lana.config import (
    BotConfig,
    MariaDBConfig,
    create_bot_config,
    create_mariadb_config,
)
from lana.logging_util import setup_logger
from lana.utils import db

logger = logging.getLogger(__name__)


def init_bot(bot_config: BotConfig, mariadb_config: MariaDBConfig):
    lana = LanaAR(config=bot_config, db_config=mariadb_config)
    try:
        logger.info("Connecting to panel database...")
        lana.panel = db.DB(db.mariadb_pool(1, json.load(open("private/config/private.json"))))
    except FileNotFoundError:
        logger.warning("No panel database config found, continuing without it.")
        pass
    lana.run(lana.config.token)


def parse_api_string(api_string):
    tmp = api_string.split(":")
    return tmp[0].split("//")[0], tmp[1].split("/")[0]


def check_api(api_url: str):
    try:
        logger.info("Checking API health...")
        response = requests.get(api_url + "/health")
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logger.error(f"API health check failed: {e}")
        return False
    return True


def main(bot_config: BotConfig, mariadb_config: MariaDBConfig, api_url: str):
    logger.info("Checking API Health...")
    if not check_api(api_url):
        logger.warning("API is not healthy, starting up on a background thread.. Please wait..")
        host, port = parse_api_string(api_url)
        threading.Thread(target=api_main, args=(host, port, bot_config.prefix_limit)).start()
        time.sleep(10)  # Might wanna do some better waiting here
        if not check_api(api_url):
            raise Exception("API is still not healthy, exiting...")
    logger.info("Starting Lana...")
    init_bot(bot_config, mariadb_config)


if __name__ == "__main__":
    args = parse_args()
    setup_logger(
        level=args.log_level if args.log_level else int(os.getenv("LOGGING_LEVEL", 20)),
        stream_logs=args.console_log if args.console_log != None else bool(os.getenv("STREAM_LOGS", False)),
    )
    main(create_bot_config(args), create_mariadb_config(args), api_url=args.api_url)
