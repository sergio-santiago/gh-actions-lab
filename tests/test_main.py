"""Tests for the application CLI."""

import pytest

from app.main import main


def test_cli_add(capsys):
    exit_code = main(["add", "2", "3"])
    assert exit_code == 0
    assert capsys.readouterr().out.strip() == "5.0"


def test_cli_div_zero(capsys):
    exit_code = main(["div", "1", "0"])
    captured = capsys.readouterr()
    assert exit_code == 1
    assert "Cannot divide by zero" in captured.err


def test_cli_invalid_op():
    with pytest.raises(SystemExit):
        main(["invalid", "1", "2"])
