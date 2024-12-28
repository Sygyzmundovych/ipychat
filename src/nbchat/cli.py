import sys

import click
import questionary
from IPython import start_ipython
from rich.console import Console
from rich.prompt import Confirm
from traitlets.config import Config

from .config import get_api_key_from_env, load_config, save_config
from .models import AVAILABLE_MODELS, get_model_by_name, get_models_by_provider
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
@click.pass_context
def app(ctx):
    """nbchat CLI application."""
    if ctx.invoked_subcommand is None:
        ctx.invoke(start)


@app.command()
def init():
    """Initialize nbchat configuration."""
    existing_config = load_config()

    console.print("\n[bold]Welcome to nbchat configuration[/bold]\n")
    display_model_table()

    model_names = [m.name for m in AVAILABLE_MODELS]
    model = select_with_arrows(
        "Which model would you like to use?",
        model_names,
    )

    model_config = get_model_by_name(model)
    provider = model_config.provider

    existing_api_key = (
        existing_config.get(provider, {}).get("api_key")
        if provider in existing_config
        else None
    )
    if existing_api_key:
        if Confirm.ask(f"Found existing {provider} API key. Keep it?"):
            api_key = existing_api_key
        else:
            api_key = get_api_key(provider)
    else:
        api_key = get_api_key(provider)

    config = {
        "current": {
            "provider": provider,
            "model": model,
        },
        "openai": {
            **(existing_config.get("openai", {})),
            "api_key": api_key
            if provider == "openai"
            else existing_config.get("openai", {}).get("api_key"),
            "max_tokens": model_config.default_max_tokens
            if provider == "openai"
            else existing_config.get("openai", {}).get("max_tokens"),
            "temperature": model_config.default_temperature
            if provider == "openai"
            else existing_config.get("openai", {}).get("temperature"),
        },
        "anthropic": {
            **(existing_config.get("anthropic", {})),
            "api_key": api_key
            if provider == "anthropic"
            else existing_config.get("anthropic", {}).get("api_key"),
        },
    }

    save_config(config)


@app.command()
def start():
    """Start the nbchat CLI application."""
    c = Config()
    c.InteractiveShellApp.extensions = ["nbchat.magic"]

    sys.argv = [sys.argv[0]]

    console.print("Welcome to nbchat! Use %chat to interact with the AI assistant.")
    console.print("You can change models using %chat_config model")
    start_ipython(config=c)


if __name__ == "__main__":
    app()
