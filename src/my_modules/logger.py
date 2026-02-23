__all__ = ["log", "console"]

import logging

from rich.console import Console
from rich.logging import RichHandler

console = Console(highlighter=None)

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%Y-%m-%d %H:%M:%S]",
    handlers=[
        RichHandler(
            console=console,
            markup=True,
            highlighter=None,
            rich_tracebacks=True,
            omit_repeated_times=False,
            tracebacks_show_locals=True,
        )
    ],
)

log = logging.getLogger(__name__)

if __name__ == "__main__":
    log.debug("This is a debug message.")
    log.info("This is a info message.")
    log.warning("This is a warning message.")
    log.error("This is a error message.")
    log.fatal("This is a critical message.")
    