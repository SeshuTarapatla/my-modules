__all__ = ["console"]

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

    def input_(self, message: str) -> str:
        self.print(f"[bold magenta]PROMPT[/]  : {message}")
        return self.input("[bold cyan]INPUT[/]   : ")


console = CustomConsole(highlighter=None)
