import logging
import sys
from pathlib import Path
from types import TracebackType

logger = logging.getLogger(__name__)

LOGGER_FORMAT = "%(asctime)s %(levelname)s %(name)s %(message)s"


def setup_logger(
    level: int = logging.INFO,
    stream_logs: bool = False,
    log_file: Path | None = None,
    err_file: Path | None = None,
    additional_handlers: list[logging.Handler] | None = None,
    logger_format: str = LOGGER_FORMAT,
) -> None:
    """Sets up the service logger

    Parameters
    ----------
    level : int, optional
        Level to log in the main logger, by default logging.INFO
    stream_logs : bool, optional
        Flag to stream the logs to the console, by default False
    log_file : Path, optional
        Default logger file path, by default LOG_FILE
    err_file : Path, optional
        Error logger file path, by default ERR_FILE
    logger_format : str, optional
        Format the logger will log in, by default LOGGER_FORMAT
    """
    log_formatter = logging.Formatter(logger_format)

    handlers: list[logging.Handler] = []
    if stream_logs:
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(log_formatter)
        stream_handler.setLevel(level)
        handlers.append(stream_handler)

    if log_file:
        handler = logging.FileHandler(log_file, mode="w")
        handler.setFormatter(log_formatter)
        handler.setLevel(level)
        handlers.append(handler)

    if err_file:
        err_handler = logging.FileHandler(err_file, mode="w")
        err_handler.setFormatter(log_formatter)
        err_handler.setLevel(logging.ERROR)
        handlers.append(err_handler)

    if additional_handlers:
        handlers.extend(additional_handlers)

    logging.basicConfig(level=level, handlers=handlers)


def log_uncaught_exceptions(
    exc_type: type[BaseException],
    exc_value: BaseException,
    exc_traceback: TracebackType,
) -> None:
    """Helper function to attach to `sys.excepthook` which will log all unexpected/uncaught exceptions before crashing"""
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    logger.critical("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
