# -*- coding: utf-8 -*-

from abc import ABC, abstractmethod
from typing import Any, Dict, Generator

from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown as RichMarkdown
from rich.panel import Panel


class BaseProvider(ABC):
    def __init__(self, config: Dict[str, Any], debug: bool = True):
        self.config = config
        self.debug = debug
        self.console = Console()

    @abstractmethod
    def initialize_client(self) -> None:
        """Initialize the API client."""
        pass

    @abstractmethod
    def stream_chat(
        self, system_prompt: str, user_content: str
    ) -> Generator[str, None, None]:
        """Stream chat responses."""
        pass

    def display_debug_info(self, system_prompt: str, user_content: str) -> None:
        """Display debug information before making API call."""
        if not self.debug:
            return

        provider_name = self.__class__.__name__.replace("Provider", "")
        self.console.print(
            f"\n[bold blue]Sending messages to {provider_name}:[/bold blue]"
        )
        self.console.print(
            Panel(
                system_prompt,
                title="[yellow]SYSTEM[/yellow]",
                border_style="yellow",
            )
        )
        self.console.print(
            Panel(
                user_content,
                title="[green]USER[/green]",
                border_style="green",
            )
        )
        self.console.print()

    def stream_response(self, system_prompt: str, user_content: str) -> None:
        """Stream responses with live display."""
        self.display_debug_info(system_prompt, user_content)

        if self.client is None:
            self.console.print(
                f"[red]Set [bold]{self.config['current']['provider'].upper()}_API_KEY[/bold] in your environment, or run [bold]ipychat config[/bold].[/red]"
            )
            return

        full_response = ""
        with Live(RichMarkdown(""), refresh_per_second=10) as live:
            for content in self.stream_chat(system_prompt, user_content):
                full_response += content
                live.update(RichMarkdown(full_response))
