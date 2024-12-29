# -*- coding: utf-8 -*-

from unittest.mock import patch

from rich.table import Table

from ipychat.ui import display_model_table, select_with_arrows


def test_display_model_table(capsys):
    with patch("ipychat.ui.console.print") as mock_print:
        display_model_table()
        assert mock_print.call_count == 1
        table = mock_print.call_args[0][0]
        assert isinstance(table, Table)
        assert table.title == "Available Models"


def test_select_with_arrows():
    choices = ["option1", "option2"]
    with patch("questionary.select") as mock_select:
        mock_select.return_value.ask.return_value = "option1"
        result = select_with_arrows("test prompt", choices)
        assert result == "option1"

        mock_select.assert_called_once()
        args, kwargs = mock_select.call_args
        assert kwargs["choices"] == choices
        assert kwargs["qmark"] == "•"
