# -*- coding: utf-8 -*-

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import toml

from ipychat.config import (
    get_api_key,
    get_api_key_from_env,
    get_default_config,
    load_config,
    save_config,
)


def test_get_default_config():
    config = get_default_config()
    assert "current" in config
    assert "provider" in config["current"]
    assert "model" in config["current"]
    assert "openai" in config
    assert "api_key" in config["openai"]
    assert "max_tokens" in config["openai"]
    assert "temperature" in config["openai"]
    assert "anthropic" in config
    assert "api_key" in config["anthropic"]


def test_load_config(mock_config_file, monkeypatch):
    monkeypatch.setattr("ipychat.config.get_config_file", lambda: mock_config_file)
    config = load_config()
    assert config["current"]["provider"] == "openai"
    assert config["openai"]["api_key"] == "test-openai-key"


def test_load_config_no_file(tmp_path: Path, monkeypatch):
    config_file = tmp_path / "config.toml"
    monkeypatch.setattr("ipychat.config.get_config_file", lambda: config_file)

    config = load_config()
    assert config == get_default_config()
    assert config_file.exists()


def test_save_config(tmp_path: Path, mock_config, monkeypatch):
    config_file = tmp_path / "config.toml"
    monkeypatch.setattr("ipychat.config.get_config_file", lambda: config_file)

    save_config(mock_config)

    assert config_file.exists()
    loaded_config = toml.load(config_file)
    assert loaded_config == mock_config


def test_get_api_key_from_env(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    assert get_api_key_from_env("openai") == "test-key"
    assert get_api_key_from_env("nonexistent") is None


def test_get_api_key_from_env_first(mock_config, monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "env-key")
    with patch("rich.prompt.Confirm.ask", return_value=True):
        api_key = get_api_key("openai", mock_config)
        assert api_key == "env-key"


def test_get_api_key_from_config(mock_config, monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    mock_config["openai"]["api_key"] = "config-key"
    with patch("rich.prompt.Confirm.ask", return_value=True):
        api_key = get_api_key("openai", mock_config)
        assert api_key == "config-key"


def test_get_api_key_from_prompt(mock_config, monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    mock_config["openai"]["api_key"] = ""
    mock_password = MagicMock()
    mock_password.ask.return_value = "prompt-key"
    with patch("questionary.password", return_value=mock_password):
        api_key = get_api_key("openai", mock_config)
        assert api_key == "prompt-key"
