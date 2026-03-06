import logging
from typing import TypeAlias

from rich.logging import RichHandler

from my_modules.console import console

LogLevel: TypeAlias = int | str

def get_logger(
    name: str = __name__, level: LogLevel = logging.INFO, propagate: bool = False
) -> logging.Logger:
    """
    Configure and return a logger with enhanced formatting using Rich library.

    Args:
        name: Name of the logger. Defaults to the module __name__ where the logger is being created.
        level: Logging level (e.g., logging.INFO, logging.DEBUG, etc.).
            Can be either an integer or string representation of the logging level.
        propagate: Boolean indicating whether log messages should be propagated to
            handlers higher in the logger hierarchy. Defaults to False.

    Returns:
        logging.Logger: Configured logger instance with RichHandler attached.
    """

    logger = logging.getLogger(name)
    if not logger.handlers:
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
        logger.propagate = propagate
    return logger
