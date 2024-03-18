import os

from lana.args_util import parse_args
from lana.logging_util import setup_logger


def init_bot(token):
    lana = LanaAR()
    try:
        lana.panel = db.DB(db.mariadb_pool(1, "private/config/private_db.json"))
    except FileNotFoundError:
        pass
    lana.run(lana.config.token)


def main():

    if args.discord_token:
        init_bot(args.discord_token, bot)
    else:
        init_bot(os.getenv("DISCORD_TOKEN"), bot)


if __name__ == "__main__":
    args = parse_args()
    setup_logger(
        level=args.log_level if args.log_level else int(os.getenv("LOGGING_LEVEL", 20)),
        stream_logs=args.console_log if args.console_log != None else bool(os.getenv("STREAM_LOGS", False)),
    )
    main()
