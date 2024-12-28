# -*- coding: utf-8 -*-

from pathlib import Path
from typing import Any, Dict

import pytest


@pytest.fixture
def mock_config() -> Dict[str, Any]:
    return {
        "current": {
            "provider": "openai",
            "model": "gpt-4o",
        },
        "openai": {
            "api_key": "test-openai-key",
            "max_tokens": 2000,
            "temperature": 0.7,
        },
        "anthropic": {
            "api_key": "test-anthropic-key",
        },
    }


@pytest.fixture
def mock_config_file(tmp_path: Path, mock_config):
    import toml

    config_file = tmp_path / "config.toml"
    with open(config_file, "w") as f:
        toml.dump(mock_config, f)
    return config_file
