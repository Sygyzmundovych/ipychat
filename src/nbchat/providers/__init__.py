# -*- coding: utf-8 -*-

from typing import Any, Dict, Type

from .anthropic import AnthropicProvider
from .base import BaseProvider
from .openai import OpenAIProvider

PROVIDER_MAP = {
    "openai": OpenAIProvider,
    "anthropic": AnthropicProvider,
}


def get_provider(config: Dict[str, Any], debug: bool = True) -> BaseProvider:
    """Get the appropriate provider based on configuration."""
    provider_name = config.get("current", {}).get("provider", "openai")
    provider_class = PROVIDER_MAP.get(provider_name)
    if not provider_class:
        raise ValueError(f"Unknown provider: {provider_name}")

    provider = provider_class(config, debug)
    provider.initialize_client()
    return provider
