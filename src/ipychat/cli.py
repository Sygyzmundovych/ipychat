# -*- coding: utf-8 -*-

import sys
from typing import Any, Dict

import click
from IPython import start_ipython
from rich.console import Console
from rich.prompt import Confirm
from traitlets.config import Config

from .config import get_api_key, load_config, save_config
from .models import AVAILABLE_MODELS, get_model_by_name
from .ui import display_model_table, select_with_arrows

console = Console()


@click.group(invoke_without_command=True)
@click.option("--debug", is_flag=True, help="Start ipychat in debug mode")
@click.pass_context
def app(ctx, debug):
    """ipychat CLI application."""
    # Store debug in the context
    ctx.ensure_object(dict)
    ctx.obj["debug"] = debug

    if ctx.invoked_subcommand is None:
        ctx.invoke(start)


@app.command()
def config():
    """Initialize ipychat configuration."""
    ipychat_config = load_config()

    console.print("\n[bold]Welcome to ipychat configuration[/bold]\n")
    display_model_table()

    model_names = [m.name for m in AVAILABLE_MODELS]
    model = select_with_arrows(
        "Which model would you like to use?",
        model_names,
    )

    model_config = get_model_by_name(model)
    provider = model_config.provider
    ipychat_config["current"] = {
        "provider": provider,
        "model": model,
    }

    api_key = get_api_key(provider, ipychat_config)
    ipychat_config[provider]["api_key"] = api_key

    save_config(ipychat_config)


@app.command(hidden=True)
@click.pass_context
def start(ctx):
    """Start the ipychat CLI application."""
    c = Config()
    c.InteractiveShellApp.extensions = ["ipychat.magic"]
    c.IPyChatMagics = Config()
    c.IPyChatMagics.debug = ctx.obj["debug"]

    sys.argv = [sys.argv[0]]

    ipychat_config = load_config()
    current_model = ipychat_config.get("current", {}).get("model")

    if current_model:
        console.print(f"Welcome to ipychat! Use %ask to chat with {current_model}.")
    else:
        console.print("Welcome to ipychat! No model configured.")
    console.print("You can change models using %models.")
    start_ipython(config=c)


if __name__ == "__main__":
    app()
