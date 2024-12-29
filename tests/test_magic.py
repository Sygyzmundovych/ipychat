# -*- coding: utf-8 -*-

from unittest.mock import Mock, patch

import pytest
from IPython.core.interactiveshell import InteractiveShell
from traitlets.config import Config

from ipychat.magic import IPyChatMagics


@pytest.fixture
def ipython():
    config = Config()
    config.IPyChatMagics = Config()
    config.IPyChatMagics.debug = False

    # Create a new instance each time
    shell = InteractiveShell.clear_instance()
    shell = InteractiveShell.instance(config=config)
    return shell


@pytest.fixture
def magic(ipython):
    with patch("ipychat.magic.get_provider") as mock_get_provider:
        mock_provider = Mock()
        mock_get_provider.return_value = mock_provider
        magic = IPyChatMagics(ipython)
        magic.provider = mock_provider
        return magic


def test_models_display(magic, capsys, mock_config_file):
    magic._config = {
        "current": {
            "provider": "openai",
            "model": "gpt-4o",
        },
        "openai": {
            "temperature": 0.7,
            "max_tokens": 2000,
            "api_key": "test-key",
        },
    }

    mock_provider = Mock()
    with (
        patch("ipychat.magic.get_provider") as mock_get_provider,
        patch("questionary.select") as mock_select,
        patch("ipychat.config.get_config_file", return_value=mock_config_file),
    ):
        mock_get_provider.return_value = mock_provider
        mock_select.return_value.ask.return_value = "gpt-4o"

        magic.models("")

        captured = capsys.readouterr()
        assert "Current configuration:" in captured.out
        assert "Provider: openai" in captured.out
        assert "Model: gpt-4o" in captured.out


def test_chat_config_model_change(magic, mock_config_file):
    magic._config = {
        "current": {
            "provider": "anthropic",
            "model": "claude-3-5-sonnet-20240620",
        },
        "anthropic": {
            "max_tokens": 2000,
            "api_key": "test-key",
        },
    }

    mock_provider = Mock()
    with (
        patch("ipychat.magic.get_provider") as mock_get_provider,
        patch("questionary.select") as mock_select,
        patch("ipychat.config.get_config_file", return_value=mock_config_file),
    ):
        mock_get_provider.return_value = mock_provider
        mock_select.return_value.ask.return_value = "gpt-4o"

        magic.models("")

        assert mock_select.called
        assert magic._config["current"]["model"] == "gpt-4o"
        assert mock_get_provider.called


def test_chat_query(magic):
    mock_provider = Mock()
    mock_provider.stream_response.return_value = ["Mock response"]
    magic.provider = mock_provider

    # Create a proper mock for the shell and history manager
    magic.shell = Mock()
    magic.shell.user_ns = {}
    magic.shell.history_manager = Mock()
    magic.shell.history_manager.input_hist_raw = [
        "",
        "command1",
        "command2",
    ]  # First entry is empty

    magic.ask("test query")

    assert mock_provider.stream_response.called
    args = mock_provider.stream_response.call_args[0]
    assert "test query" in args[1]


def test_magic_debug_from_config(ipython):
    """Test that debug flag is properly set from IPython config."""
    config = Config()
    config.IPyChatMagics = Config()
    config.IPyChatMagics.debug = True

    shell = InteractiveShell.clear_instance()
    shell = InteractiveShell.instance(config=config)

    with patch("ipychat.magic.get_provider") as mock_get_provider:
        magic = IPyChatMagics(shell)
        assert magic.debug is True
        mock_get_provider.assert_called_with(magic._config, True)


def test_magic_debug_affects_provider(magic):
    """Test that debug setting affects provider behavior."""
    from IPython.core.history import HistoryManager

    magic.shell.history_manager = HistoryManager(shell=magic.shell)
    magic.shell.history_manager.input_hist_raw = ["", "command1"]
    magic.debug = True

    magic.ask("test query")

    assert magic.provider.stream_response.called
    assert magic.debug is True


def test_magic_debug_inheritance(ipython):
    """Test that debug setting is properly inherited from Configurable."""
    config = Config()
    config.IPyChatMagics = Config()
    config.IPyChatMagics.debug = True

    shell = InteractiveShell.clear_instance()
    shell = InteractiveShell.instance(config=config)

    with patch("ipychat.magic.get_provider"):
        magic = IPyChatMagics(shell)
        assert magic.debug is True

        config.IPyChatMagics.debug = False
        shell = InteractiveShell.clear_instance()
        shell = InteractiveShell.instance(config=config)
        magic = IPyChatMagics(shell)
        assert magic.debug is False
