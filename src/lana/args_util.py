#!/usr/bin/env python

import logging
import os
from argparse import ArgumentParser
from dataclasses import dataclass
from typing import OrderedDict

logger = logging.getLogger(__name__)


def add_boolean_arg(parser: ArgumentParser, name: str, desc: str, default: bool = False) -> None:
    """Adds a boolean arg to the arg parser allowing --arg and --no-arg for True and False respectively

    Parameters
    ----------
    parser : ArgumentParser
        Arg parser to add the argument to
    name : str
        Name of the argument
    desc : str
        Description of the arg to add
    default : bool, optional
        Default value of the boolean flag, by default False
    """
    dest = name.replace("-", "_")
    group = parser.add_argument_group(f"{name} options:", desc)
    me_group = group.add_mutually_exclusive_group(required=False)
    me_group.add_argument(f"--{name}", dest=dest, action="store_true", help="(default)" if default else "")
    me_group.add_argument(
        f"--no-{name}",
        dest=dest,
        action="store_false",
        help="(default)" if not default else "",
    )
    parser.set_defaults(**{dest: default})


@dataclass
class Args:
    """Data Class for storing CL args"""

    owners = os.getenv("OWNERS", None)
    prefix_limit = os.getenv("PREFIX_LIMIT", 25)
    error_channel = os.getenv("ERROR_CHANNEL", None)
    output_channel = os.getenv("OUTPUT_CHANNEL", None)
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", 3306)
    db_user = os.getenv("DB_USER", None)
    db_password = os.getenv("DB_PASSWORD", None)
    db_database = os.getenv("DB_DATABASE", None)
    db_pool_size = os.getenv("DB_POOL_SIZE", 20)
    token = os.getenv("DISCORD_TOKEN", None)
    api_url = os.getenv("API_URL", "http://localhost:4004/api")
    log_level = os.getenv("LOGGING_LEVEL", logging.INFO)
    console_log = os.getenv("STREAM_LOGS", True)


def parse_args() -> Args:
    """Parses CL args into a Args object

    Returns
    -------
    Args
        Args object containing all the
    """
    arg_parser = ArgumentParser()
    arg_parser.add_argument("-o", "--owners", required=True, help="Comma separated list of bot owners")
    arg_parser.add_argument("-pl", "--prefix-limit", default=25, help="The prefix limit of the bot")
    arg_parser.add_argument("-ec", "--error-channel", help="The channel to log errors to")
    arg_parser.add_argument("-oc", "--output-channel", help="The channel to log output to")
    arg_parser.add_argument("-dh", "--db-host", default="localhost", help="The host of the database")
    arg_parser.add_argument("-dp", "--db-port", default=3306, help="The port of the database")
    arg_parser.add_argument("-du", "--db-user", help="The user of the database")
    arg_parser.add_argument("-dpw", "--db-password", help="The password of the database")
    arg_parser.add_argument("-ddb", "--db-database", help="The database to connect to")
    arg_parser.add_argument("-dps", "--db-pool-size", default=20, help="The pool size of the database")
    arg_parser.add_argument("-t", "--token", required=True, help="The bot token")
    arg_parser.add_argument("-au", "--api-url", default="http://localhost:4004/api", help="The API url to connect to")
    arg_parser.add_argument(
        "-ll",
        "--log-level",
        default=logging.INFO,
        type=int,
        dest="log_level",
        help="The log level of logging",
    )
    add_boolean_arg(arg_parser, "console-log", "Log to console", default=True)

    return Args(**OrderedDict(vars(arg_parser.parse_args())))
