# -*- coding: utf-8 -*-

import os
from pathlib import Path
from typing import Any, Dict, Optional, Union

import toml
from click import get_app_dir
from rich.console import Console

console = Console()


def get_api_key_from_env(provider: str) -> Optional[str]:
    """Get API key from environment variable."""
    return os.getenv(f"{provider.upper()}_API_KEY")


def get_config_file() -> Path:
    """Get the path to the config file."""
    config_dir = Path(get_app_dir("ipychat"))
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir / "config.toml"


def load_config() -> Dict[str, Any]:
    """Load configuration from TOML file."""
    config_file = get_config_file()

    if not config_file.exists():
        return {}

    try:
        with open(config_file) as f:
            return toml.load(f)
    except Exception as e:
        console.print(f"[yellow]Warning: Could not load existing config: {e}[/yellow]")
        return {}


def save_config(config: Dict[str, Any]) -> None:
    """Save configuration to TOML file."""
    config_file = get_config_file()

    with open(config_file, "w") as f:
        toml.dump(config, f)
