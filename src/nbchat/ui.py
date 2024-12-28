# -*- coding: utf-8 -*-

from typing import List

import questionary
from rich.console import Console
from rich.prompt import Confirm
from rich.table import Table

from .models import AVAILABLE_MODELS

console = Console()


def display_model_table():
    """Display available models in a table."""
    table = Table(title="Available Models")
    table.add_column("Provider")
    table.add_column("Model")

    for model in AVAILABLE_MODELS:
        table.add_row(model.provider, model.name)

    console.print(table)


def select_with_arrows(prompt: str, choices: List[str]) -> str:
    """Select an option using arrow keys."""
    return questionary.select(
        prompt,
        choices=choices,
        qmark="•",
        pointer=">",
        style=questionary.Style(
            [
                ("highlighted", "bold fg:ansiblue"),
            ]
        ),
    ).ask()
