# -*- coding: utf-8 -*-

import os
from pathlib import Path
from typing import Any, Dict, Optional, Union

import questionary
import toml
from click import get_app_dir
from rich.console import Console
from rich.prompt import Confirm

console = Console()


def get_default_config() -> Dict[str, Any]:
    from .models import AVAILABLE_MODELS

    DEFAULT_MODEL = AVAILABLE_MODELS[0]
    DEFAULT_CONFIG = {
        "current": {
            "provider": DEFAULT_MODEL.provider,
            "model": DEFAULT_MODEL.name,
        },
        "openai": {
            "api_key": "",
            "max_tokens": DEFAULT_MODEL.default_max_tokens,
            "temperature": DEFAULT_MODEL.default_temperature,
        },
        "anthropic": {"api_key": ""},
    }

    return DEFAULT_CONFIG


def get_api_key_from_env(provider: str) -> Optional[str]:
    """Get API key from environment variable."""
    return os.getenv(f"{provider.upper()}_API_KEY")


def get_api_key(provider: str, ipychat_config: Dict[str, Any]) -> str:
    env_api_key = get_api_key_from_env(provider)

    if env_api_key:
        if Confirm.ask(
            f"Found {provider.upper()}_API_KEY in environment. Use this API key?",
            default=True,
        ):
            return env_api_key

    config_api_key = (
        ipychat_config.get(provider, {}).get("api_key")
        if provider in ipychat_config
        else None
    )
    if config_api_key:
        if Confirm.ask(f"Found existing {provider} API key. Keep it?", default=True):
            return config_api_key

    return questionary.password(f"Enter your {provider} API key:", qmark="•").ask()


def get_config_file() -> Path:
    """Get the path to the config file."""
    config_dir = Path(get_app_dir("ipychat"))
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir / "config.toml"


def load_config() -> Dict[str, Any]:
    """Load configuration from TOML file."""

    config_file = get_config_file()

    if not config_file.exists():
        default_config = get_default_config()
        save_config(default_config)
        return default_config

    with open(config_file) as f:
        config = toml.load(f)

    current_provider = config["current"]["provider"]
    config[current_provider]["api_key"] = get_api_key_from_env(current_provider)

    return config


def save_config(config: Dict[str, Any]) -> None:
    """Save configuration to TOML file."""
    config_file = get_config_file()

    with open(config_file, "w") as f:
        toml.dump(config, f)
