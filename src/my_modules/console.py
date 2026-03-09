"""Custom console module providing enhanced logging functionality.

This module extends the Rich Console class to provide custom logging methods
with colored output and additional features for debugging and user interaction.

Exports:
    console: An instance of CustomConsole ready for use
"""

__all__ = ["console"]

from sys import exit
from typing import NoReturn, overload

from rich.console import Console


class CustomConsole(Console):
    """A custom console class extending Rich's Console with enhanced logging methods.

    This class provides color-coded logging methods for different log levels
    (debug, info, warning, error) and a custom input logging method.

    Attributes:
        Inherits all attributes from rich.console.Console
    """

    def debug(self, message: str):
        """Log a debug message with green color formatting.

        Args:
            message: The debug message to display
        """
        self.print(f"[bold green]DEBUG[/]   : {message}")

    def info(self, message: str):
        """Log an informational message with blue color formatting.

        Args:
            message: The informational message to display
        """
        self.print(f"[bold blue]INFO[/]    : {message}")

    def warning(self, message: str):
        """Log a warning message with yellow color formatting.

        Args:
            message: The warning message to display
        """
        self.print(f"[bold yellow]WARNING[/] : {message}")

    @overload
    def error(self, message: str, kill: int) -> NoReturn: ...

    @overload
    def error(self, message: str, kill: None) -> None: ...

    def error(self, message: str, kill: int | None = None) -> None | NoReturn:
        """Log an error message with red color formatting and optionally exit.

        Args:
            message: The error message to display
            kill: Optional exit code to terminate the program with
        """
        self.print(f"[bold red]ERROR[/]   : {message}")
        if isinstance(kill, int):
            exit(kill)

    @overload
    def log_input(self, message: str) -> str: ...

    @overload
    def log_input(
        self, message: str, tag: str = "PROMPT", color: str = "magenta"
    ) -> str: ...

    def log_input(
        self, message: str, tag: str = "PROMPT", color: str = "magenta"
    ) -> str:
        """Display a prompt message and get user input with customizable formatting.

        Args:
            message: The prompt message to display
            tag: The tag/label for the prompt (default: "PROMPT")
            color: The color for the prompt tag (default: "magenta")

        Returns:
            The user's input as a string
        """
        self.print(f"[bold {color}]{tag.ljust(7)}[/] : {message}")
        return self.input("[bold cyan]INPUT[/]   : ")


console = CustomConsole(highlighter=None)
