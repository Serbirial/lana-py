from dataclasses import dataclass


@dataclass
class BotConfig:
    """Data Class for storing Bot config"""

    token: str = None
    owners: list[int] = None
    prefix_limit: int = 25
    error_channel: int = None  # You might want to move this later so you can suport multiple servers
    output_channel: int = None
    api_url: str = "http://localhost:4004/api"


def create_bot_config(args):
    """
    Creates a BotConfig instance from Args.

    Parameters
    ----------
    args : Args
        The Args instance containing command line and environment variable settings.

    Returns
    -------
    BotConfig
        An instance of BotConfig initialized with values from Args.
    """
    return BotConfig(
        token=args.token,
        owners=[int(owner) for owner in args.owners.split(",")],
        prefix_limit=int(args.prefix_limit),
        error_channel=int(args.error_channel),
        output_channel=int(args.output_channel),
        api_url=args.api_url,
    )


@dataclass
class MariaDBConfig:
    """Data Class for storing MariaDB config"""

    host: str = "localhost"
    port: int = 3306
    user: str = None
    password: str = None
    database: str = None
    pool_size: int = 20
    pool_name: str = None


def create_mariadb_config(args):
    """
    Creates a MariaDBConfig instance from Args.

    Parameters
    ----------
    args : Args
        The Args instance containing command line and environment variable settings.

    Returns
    -------
    MariaDBConfig
        An instance of MariaDBConfig initialized with values from Args.
    """
    return MariaDBConfig(
        host=args.db_host,
        port=int(args.db_port),  # Ensure port is an integer
        user=args.db_user,
        password=args.db_password,
        database=args.db_database,
        pool_size=int(args.db_pool_size),  # Ensure pool_size is an integer
        pool_name="default_pool",  # Assuming a default pool name; adjust as necessary
    )


@dataclass
class DashboardConfig:
    """Data Class for storing  Dashboard config"""

    client_id: str = None
    client_secret: str = None
    callback_url: str = None
