# -*- coding: utf-8 -*-

from unittest.mock import Mock, patch

import pytest
from IPython.core.interactiveshell import InteractiveShell
from traitlets.config import Config

from nbchat.config import save_config
from nbchat.magic import NBChatMagics


@pytest.fixture
def ipython():
    config = Config()
    config.NBChatMagics = Config()
    config.NBChatMagics.debug = False

    # Create a new instance each time
    shell = InteractiveShell.clear_instance()
    shell = InteractiveShell.instance(config=config)
    return shell


@pytest.fixture
def magic(ipython):
    return NBChatMagics(ipython)


def test_chat_config_display(magic, capsys, mock_config_file):
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
        patch("nbchat.magic.get_provider") as mock_get_provider,
        patch("questionary.select") as mock_select,
        patch("nbchat.config.get_config_file", return_value=mock_config_file),
    ):
        mock_get_provider.return_value = mock_provider
        mock_select.return_value.ask.return_value = "gpt-4o"

        magic.chat_config("")

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
        patch("nbchat.magic.get_provider") as mock_get_provider,
        patch("questionary.select") as mock_select,
        patch("nbchat.config.get_config_file", return_value=mock_config_file),
    ):
        mock_get_provider.return_value = mock_provider
        mock_select.return_value.ask.return_value = "gpt-4o"

        magic.chat_config("")

        assert mock_select.called
        assert magic._config["current"]["model"] == "gpt-4o"
        assert mock_get_provider.called


def test_chat_query(magic):
    mock_provider = Mock()
    mock_provider.stream_with_display.return_value = ["Mock response"]
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

    magic.chat("test query")

    assert mock_provider.stream_with_display.called
    args = mock_provider.stream_with_display.call_args[0]
    assert "test query" in args[1]


def test_magic_debug_from_config():
    """Test that debug flag is properly set from IPython config."""
    config = Config()
    config.NBChatMagics = Config()
    config.NBChatMagics.debug = True

    shell = InteractiveShell.clear_instance()
    shell = InteractiveShell.instance(config=config)

    # Initialize magic with debug config
    magic = NBChatMagics(shell)
    assert magic.debug is True

    # Verify provider was initialized with debug flag
    with patch("nbchat.magic.get_provider") as mock_get_provider:
        magic = NBChatMagics(shell)
        mock_get_provider.assert_called_with(magic._config, True)


def test_magic_debug_affects_provider(ipython):
    """Test that debug setting affects provider behavior."""
    from IPython.core.history import HistoryManager

    # Create a proper history manager
    ipython.history_manager = HistoryManager(shell=ipython)
    ipython.history_manager.input_hist_raw = ["", "command1"]

    magic = NBChatMagics(ipython)

    # Set up mock provider
    mock_provider = Mock()
    magic.provider = mock_provider
    magic.debug = True

    # Test chat with debug enabled
    magic.chat("test query")

    # Verify provider was used with debug info
    assert mock_provider.stream_with_display.called
    assert magic.debug is True


def test_magic_debug_inheritance():
    """Test that debug setting is properly inherited from Configurable."""
    # Create config with debug enabled
    config = Config()
    config.NBChatMagics = Config()
    config.NBChatMagics.debug = True

    # Create shell with config
    shell = InteractiveShell.clear_instance()
    shell = InteractiveShell.instance(config=config)

    # Initialize magic
    magic = NBChatMagics(shell)
    assert magic.debug is True

    # Change config and verify it updates
    config.NBChatMagics.debug = False
    shell = InteractiveShell.clear_instance()
    shell = InteractiveShell.instance(config=config)
    magic = NBChatMagics(shell)
    assert magic.debug is False
