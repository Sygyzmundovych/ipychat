# -*- coding: utf-8 -*-

from unittest.mock import Mock, patch

import pytest
from IPython.testing.globalipapp import get_ipython

from nbchat.magic import NBChatMagics


@pytest.fixture
def ipython():
    return get_ipython()


@pytest.fixture
def magic(ipython):
    return NBChatMagics(ipython)


def test_chat_config_display(magic, capsys):
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

    # Mock the select_with_arrows call
    with patch("questionary.select") as mock_select:
        mock_select.return_value.ask.return_value = "gpt-4o"

        magic.chat_config("")

        captured = capsys.readouterr()
        assert "Current configuration:" in captured.out
        assert "Provider: openai" in captured.out
        assert "Model: gpt-4o" in captured.out


def test_chat_config_model_change(magic):
    mock_provider = Mock()
    with (
        patch("nbchat.magic.get_provider") as mock_get_provider,
        patch("questionary.select") as mock_select,
        patch("nbchat.magic.save_config") as mock_save,
    ):
        mock_get_provider.return_value = mock_provider
        mock_select.return_value.ask.return_value = "gpt-4o"

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

        magic.chat_config("")

        assert mock_select.called
        assert mock_save.called
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
