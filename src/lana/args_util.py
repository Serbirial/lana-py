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
    log_level = logging.INFO
    console_log = True


def parse_args() -> Args:
    """Parses CL args into a Args object

    Returns
    -------
    Args
        Args object containing all the
    """
    arg_parser = ArgumentParser()
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
