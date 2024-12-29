# -*- coding: utf-8 -*-

import pytest

from ipychat.models import get_current_model, get_model_by_name, get_models_by_provider


def test_get_model_by_name():
    model = get_model_by_name("gpt-4o")
    assert model.name == "gpt-4o"
    assert model.provider == "openai"

    with pytest.raises(ValueError):
        get_model_by_name("nonexistent-model")


def test_get_models_by_provider():
    openai_models = get_models_by_provider("openai")
    assert all(m.provider == "openai" for m in openai_models)
    assert len(openai_models) > 0

    anthropic_models = get_models_by_provider("anthropic")
    assert all(m.provider == "anthropic" for m in anthropic_models)
    assert len(anthropic_models) > 0


def test_get_current_model(mock_config, monkeypatch):
    monkeypatch.setattr("ipychat.models.load_config", lambda: mock_config)
    model = get_current_model()
    assert model.name == "gpt-4o"
    assert model.provider == "openai"
