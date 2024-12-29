# -*- coding: utf-8 -*-

from unittest.mock import Mock, patch

import pytest

from ipychat.providers import get_provider
from ipychat.providers.anthropic import AnthropicProvider
from ipychat.providers.openai import OpenAIProvider


def test_get_provider(mock_config):
    provider = get_provider(mock_config)
    assert isinstance(provider, OpenAIProvider)

    mock_config["current"]["provider"] = "anthropic"
    provider = get_provider(mock_config)
    assert isinstance(provider, AnthropicProvider)

    mock_config["current"]["provider"] = "invalid"
    with pytest.raises(ValueError):
        get_provider(mock_config)


def test_openai_provider_stream_chat(mock_config):
    provider = OpenAIProvider(mock_config)
    provider.initialize_client()

    mock_response = Mock()
    mock_response.choices = [Mock(delta=Mock(content="test response"))]

    with patch.object(provider.client.chat.completions, "create") as mock_create:
        mock_create.return_value = [mock_response]

        responses = list(provider.stream_chat("system prompt", "user content"))
        assert responses == ["test response"]


def test_anthropic_provider_stream_chat(mock_config):
    provider = AnthropicProvider(mock_config)
    provider.initialize_client()

    mock_chunk = Mock()
    mock_chunk.type = "content_block_delta"
    mock_chunk.delta = Mock(text="test response")

    with patch.object(provider.client.messages, "create") as mock_create:
        mock_create.return_value = [mock_chunk]

        responses = list(provider.stream_chat("system prompt", "user content"))
        assert responses == ["test response"]


def test_openai_provider_missing_api_key(mock_config):
    # Ensure console is properly mocked
    mock_console = Mock()
    mock_config["console"] = mock_console

    # Test empty API key
    mock_config["openai"] = {"api_key": ""}
    provider = OpenAIProvider(mock_config)
    provider.console = mock_console
    provider.initialize_client()
    assert provider.client is None
    mock_console.print.assert_called_once_with(
        "[red]Set [bold]OPENAI_API_KEY[/bold] in your environment, or run [bold]ipychat config[/bold].[/red]"
    )

    # Reset mock
    mock_console.print.reset_mock()

    # Test missing API key
    mock_config["openai"] = {}
    provider = OpenAIProvider(mock_config)
    provider.console = mock_console
    provider.initialize_client()
    assert provider.client is None
    mock_console.print.assert_called_once_with(
        "[red]Set [bold]OPENAI_API_KEY[/bold] in your environment, or run [bold]ipychat config[/bold].[/red]"
    )

    # Reset mock
    mock_console.print.reset_mock()

    # Test missing openai config section
    mock_config.pop("openai", None)
    provider = OpenAIProvider(mock_config)
    provider.console = mock_console
    provider.initialize_client()
    assert provider.client is None
    mock_console.print.assert_called_once_with(
        "[red]Set [bold]OPENAI_API_KEY[/bold] in your environment, or run [bold]ipychat config[/bold].[/red]"
    )


def test_anthropic_provider_missing_api_key(mock_config):
    # Ensure console is properly mocked
    mock_console = Mock()
    mock_config["console"] = mock_console

    # Test empty API key
    mock_config["anthropic"] = {"api_key": ""}
    provider = AnthropicProvider(mock_config)
    provider.console = mock_console
    provider.initialize_client()
    assert provider.client is None
    mock_console.print.assert_called_once_with(
        "[red]Set [bold]ANTHROPIC_API_KEY[/bold] in your environment, or run [bold]ipychat config[/bold].[/red]"
    )

    # Reset mock
    mock_console.print.reset_mock()

    # Test missing API key
    mock_config["anthropic"] = {}
    provider = AnthropicProvider(mock_config)
    provider.console = mock_console
    provider.initialize_client()
    assert provider.client is None
    mock_console.print.assert_called_once_with(
        "[red]Set [bold]ANTHROPIC_API_KEY[/bold] in your environment, or run [bold]ipychat config[/bold].[/red]"
    )

    # Reset mock
    mock_console.print.reset_mock()

    # Test missing anthropic config section
    mock_config.pop("anthropic", None)
    provider = AnthropicProvider(mock_config)
    provider.console = mock_console
    provider.initialize_client()
    assert provider.client is None
    mock_console.print.assert_called_once_with(
        "[red]Set [bold]ANTHROPIC_API_KEY[/bold] in your environment, or run [bold]ipychat config[/bold].[/red]"
    )
