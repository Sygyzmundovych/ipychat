# -*- coding: utf-8 -*-

import sys

import click
import questionary
from IPython import start_ipython
from rich.console import Console
from rich.prompt import Confirm
from traitlets.config import Config

from .config import get_api_key_from_env, load_config, save_config
from .models import AVAILABLE_MODELS, get_model_by_name
from .ui import display_model_table, select_with_arrows

console = Console()


def get_api_key(provider: str) -> str:
    api_key = get_api_key_from_env(provider)

    if api_key:
        if Confirm.ask(
            f"Found {provider.upper()}_API_KEY in environment. Use this API key?"
        ):
            return api_key

    return questionary.password(f"Enter your {provider} API key:", qmark="•").ask()


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

    existing_api_key = (
        ipychat_config.get(provider, {}).get("api_key")
        if provider in ipychat_config
        else None
    )
    if existing_api_key:
        if Confirm.ask(f"Found existing {provider} API key. Keep it?", default=True):
            api_key = existing_api_key
        else:
            api_key = get_api_key(provider)
    else:
        api_key = get_api_key(provider)

    updated_ipychat_config = {
        "current": {
            "provider": provider,
            "model": model,
        },
        "openai": {
            **(ipychat_config.get("openai", {})),
            "api_key": api_key
            if provider == "openai"
            else ipychat_config.get("openai", {}).get("api_key"),
            "max_tokens": model_config.default_max_tokens
            if provider == "openai"
            else ipychat_config.get("openai", {}).get("max_tokens"),
            "temperature": model_config.default_temperature
            if provider == "openai"
            else ipychat_config.get("openai", {}).get("temperature"),
        },
        "anthropic": {
            **(ipychat_config.get("anthropic", {})),
            "api_key": api_key
            if provider == "anthropic"
            else ipychat_config.get("anthropic", {}).get("api_key"),
        },
    }

    save_config(updated_ipychat_config)


@app.command(hidden=True)
@click.pass_context
def start(ctx):
    """Start the ipychat CLI application."""
    c = Config()
    c.InteractiveShellApp.extensions = ["ipychat.magic"]
    c.IPyChatMagics = Config()
    c.IPyChatMagics.debug = ctx.obj["debug"]

    sys.argv = [sys.argv[0]]

    console.print("Welcome to ipychat! Use %ask to chat with the AI assistant.")
    console.print("You can change models using %models.")
    start_ipython(config=c)


if __name__ == "__main__":
    app()
