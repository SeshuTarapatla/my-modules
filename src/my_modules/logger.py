import logging
from typing import TypeAlias

from rich.logging import RichHandler

from my_modules.console import console

LogLevel: TypeAlias = int | str


def get_logger(
    name: str = __name__, level: LogLevel = logging.INFO, propagate: bool = False
) -> logging.Logger:
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
