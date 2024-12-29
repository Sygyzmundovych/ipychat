# -*- coding: utf-8 -*-

from pathlib import Path

import toml

from ipychat.config import get_api_key_from_env, load_config, save_config


def test_load_config(mock_config_file, monkeypatch):
    monkeypatch.setattr("ipychat.config.get_config_file", lambda: mock_config_file)
    config = load_config()
    assert config["current"]["provider"] == "openai"
    assert config["openai"]["api_key"] == "test-openai-key"


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
