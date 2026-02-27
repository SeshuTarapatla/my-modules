__all__ = ["console", "get_logger", "suppress_logger", "suppress_loggers"]

import logging
from typing import Literal

from rich.console import Console
from rich.logging import RichHandler

console = Console(highlighter=None)


def suppress_logger(
    logger: str, level: Literal["warning", "error", "fatal"] = "warning"
):
    try:
        match level:
            case "warning":
                log_level = logging.WARNING
            case "error":
                log_level = logging.ERROR
            case "fatal":
                log_level = logging.FATAL
            case _:
                log_level = logging.WARNING
        logging.getLogger(logger).setLevel(log_level)
    except Exception:
        return None


def suppress_loggers(
    *loggers: str, level: Literal["warning", "error", "fatal"] = "warning"
):
    [suppress_logger(logger, level) for logger in loggers]


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)

    if not logger.handlers:  # prevents duplicate handlers
        logger.setLevel(logging.INFO)

        handler = RichHandler(
            console=console,
            markup=True,
            highlighter=None,
            rich_tracebacks=True,
            omit_repeated_times=False,
            tracebacks_show_locals=True,
        )
        handler.setLevel(logging.INFO)
        handler.setFormatter(logging.Formatter("%(message)s"))

        logger.addHandler(handler)
        logger.propagate = True

    return logger


if __name__ == "__main__":
    log = get_logger(__name__)
    log.debug("This is a debug message.")
    log.info("This is a info message.")
    log.warning("This is a warning message.")
    log.error("This is a error message.")
    log.fatal("This is a critical message.")
