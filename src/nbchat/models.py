# -*- coding: utf-8 -*-

from dataclasses import dataclass
from typing import Dict, List, Optional

from .config import load_config


@dataclass
class ModelConfig:
    name: str
    provider: str
    default_max_tokens: Optional[int] = None
    default_temperature: Optional[float] = None


AVAILABLE_MODELS = [
    ModelConfig("gpt-4o", "openai", default_max_tokens=2000, default_temperature=0.7),
    ModelConfig("claude-3-5-sonnet-20241022", "anthropic"),
]


def get_models_by_provider(provider: str) -> List[ModelConfig]:
    return [model for model in AVAILABLE_MODELS if model.provider == provider]


def get_model_by_name(name: str) -> ModelConfig:
    for model in AVAILABLE_MODELS:
        if model.name == name:
            return model
    raise ValueError(f"Model {name} not found")


def get_current_model() -> ModelConfig:
    config = load_config()
    current = config.get("current", {})
    model_name = current.get("model")

    if not model_name:
        openai_models = get_models_by_provider("openai")
        return openai_models[0]

    return get_model_by_name(model_name)
