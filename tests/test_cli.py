# -*- coding: utf-8 -*-

from pathlib import Path
from unittest.mock import patch

import pytest
import toml
from click.testing import CliRunner

from ipychat.cli import app
from ipychat.cli import config as config_command
from ipychat.cli import start as start_command


@pytest.fixture
def cli_runner():
    return CliRunner()


@pytest.fixture
def mock_ipython():
    with patch("ipychat.cli.start_ipython") as mock:
        yield mock


def test_app_no_command(cli_runner, mock_ipython):
    """Test that running app without command invokes start."""
    result = cli_runner.invoke(app)
    assert result.exit_code == 0
    assert mock_ipython.called


def test_start_command(cli_runner, mock_ipython):
    """Test the start command."""
    # Create a context with default debug=False
    result = cli_runner.invoke(start_command, obj={"debug": False})
    assert result.exit_code == 0
    assert mock_ipython.called


def test_config_command_new_config(cli_runner, tmp_path, monkeypatch):
    """Test config command creating new configuration."""
    # Mock config directory
    config_dir = str(tmp_path)
    monkeypatch.setattr("click.get_app_dir", lambda x: config_dir)

    # Mock the config file path
    def mock_config_file():
        return Path(config_dir) / "config.toml"

    monkeypatch.setattr("ipychat.config.get_config_file", mock_config_file)

    # Mock user inputs
    with patch("questionary.select") as mock_select:
        mock_select.return_value.ask.return_value = "gpt-4o"

        with patch("questionary.password") as mock_password:
            mock_password.return_value.ask.return_value = "test-api-key"

            with patch("rich.prompt.Confirm.ask") as mock_confirm:
                mock_confirm.return_value = False

                result = cli_runner.invoke(config_command, catch_exceptions=False)

                print(f"Command output: {result.output}")
                if result.exception:
                    print(f"Exception: {result.exception}")

                config_file = tmp_path / "config.toml"

                assert result.exit_code == 0
                assert "Welcome to ipychat configuration" in result.output

                # Verify config file was created
                assert config_file.exists(), f"Config file not found at {config_file}"

                # Verify config contents
                config = toml.load(config_file)
                assert config["current"]["provider"] == "openai"
                assert config["current"]["model"] == "gpt-4o"
                assert config["openai"]["api_key"] == "test-api-key"


def test_config_command_existing_config(cli_runner, mock_config_file, monkeypatch):
    """Test config command with existing configuration."""
    # Mock config directory to use test config
    config_dir = mock_config_file.parent
    monkeypatch.setattr("click.get_app_dir", lambda x: str(config_dir))

    # Mock the config file path
    def mock_config_file_fn():
        return mock_config_file

    monkeypatch.setattr("ipychat.config.get_config_file", mock_config_file_fn)

    with patch("questionary.select") as mock_select:
        mock_select.return_value.ask.return_value = "claude-3-5-sonnet-20241022"

        with patch("rich.prompt.Confirm.ask") as mock_confirm:
            # Simulate keeping existing API key
            mock_confirm.return_value = True

            result = cli_runner.invoke(config_command, catch_exceptions=False)

            assert result.exit_code == 0

            # Verify config was updated
            config = toml.load(mock_config_file)
            assert config["current"]["provider"] == "anthropic"
            assert config["current"]["model"] == "claude-3-5-sonnet-20241022"
            # Verify OpenAI config was preserved
            assert config["openai"]["api_key"] == "test-openai-key"


def test_config_command_env_api_key(cli_runner, tmp_path, monkeypatch):
    """Test config using API key from environment."""
    config_dir = str(tmp_path)
    monkeypatch.setattr("click.get_app_dir", lambda x: config_dir)

    # Mock the config file path
    def mock_config_file():
        return Path(config_dir) / "config.toml"

    monkeypatch.setattr("ipychat.config.get_config_file", mock_config_file)

    monkeypatch.setenv("OPENAI_API_KEY", "env-api-key")

    with patch("questionary.select") as mock_select:
        mock_select.return_value.ask.return_value = "gpt-4o"

        with patch("rich.prompt.Confirm.ask") as mock_confirm:
            # Simulate using env API key
            mock_confirm.return_value = True

            result = cli_runner.invoke(config_command, catch_exceptions=False)

            assert result.exit_code == 0

            config = toml.load(tmp_path / "config.toml")
            assert config["openai"]["api_key"] == "env-api-key"


def test_config_command_error_handling(cli_runner, tmp_path, monkeypatch):
    """Test error handling in config command."""
    monkeypatch.setattr("click.get_app_dir", lambda x: str(tmp_path))

    with patch("ipychat.ui.select_with_arrows") as mock_select:
        # Simulate selection of invalid model
        mock_select.return_value = "invalid-model"

        result = cli_runner.invoke(config_command)

        assert result.exit_code != 0
        assert "Aborted!" in result.output


def test_start_command_no_config(cli_runner, tmp_path, monkeypatch, mock_ipython):
    """Test start command behavior when no config exists."""
    monkeypatch.setattr("click.get_app_dir", lambda x: str(tmp_path))

    result = cli_runner.invoke(start_command, obj={"debug": False})
    assert result.exit_code == 0
    assert mock_ipython.called


def test_cli_help(cli_runner):
    """Test CLI help output."""
    result = cli_runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "ipychat CLI application" in result.output

    result = cli_runner.invoke(config_command, ["--help"])
    assert result.exit_code == 0
    assert "Initialize ipychat configuration" in result.output

    result = cli_runner.invoke(start_command, ["--help"])
    assert result.exit_code == 0
    assert "Start the ipychat CLI application" in result.output


def test_app_debug_flag(cli_runner, mock_ipython):
    """Test that debug flag is properly passed through the CLI."""
    result = cli_runner.invoke(app, ["--debug"])
    assert result.exit_code == 0

    # Verify debug flag was passed to IPython config
    config = mock_ipython.call_args[1]["config"]
    assert config.IPyChatMagics.debug is True


def test_start_command_with_debug(cli_runner, mock_ipython):
    """Test start command with debug flag."""
    result = cli_runner.invoke(start_command, obj={"debug": True})
    assert result.exit_code == 0

    # Verify IPython configuration
    config = mock_ipython.call_args[1]["config"]
    assert config.IPyChatMagics.debug is True
    assert "ipychat.magic" in config.InteractiveShellApp.extensions


def test_start_command_without_debug(cli_runner, mock_ipython):
    """Test start command without debug flag."""
    result = cli_runner.invoke(start_command, obj={"debug": False})
    assert result.exit_code == 0

    # Verify IPython configuration
    config = mock_ipython.call_args[1]["config"]
    assert config.IPyChatMagics.debug is False
