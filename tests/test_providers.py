# -*- coding: utf-8 -*-

from unittest.mock import Mock, patch

import pytest

from nbchat.providers import get_provider
from nbchat.providers.anthropic import AnthropicProvider
from nbchat.providers.openai import OpenAIProvider


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
