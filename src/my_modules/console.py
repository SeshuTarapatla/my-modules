__all__ = ["console"]

from typing import overload

from rich.console import Console


class CustomConsole(Console):
    def debug(self, message: str):
        self.print(f"[bold green]DEBUG[/]   : {message}")

    def info(self, message: str):
        self.print(f"[bold blue]INFO[/]    : {message}")

    def warning(self, message: str):
        self.print(f"[bold yellow]WARNING[/] : {message}")

    def error(self, message: str):
        self.print(f"[bold red]ERROR[/]   : {message}")

    @overload
    def log_input(self, message: str) -> str: ...

    @overload
    def log_input(
        self, message: str, tag: str = "PROMPT", color: str = "magenta"
    ) -> str: ...

    def log_input(self, message: str, tag: str = "PROMPT", color: str = "magenta") -> str:
        self.print(f"[bold {color}]{tag.ljust(7)}[/] : {message}")
        return self.input("[bold cyan]INPUT[/]   : ")


console = CustomConsole(highlighter=None)
