import logging
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from utils.logger import setup_logger


@pytest.fixture
def mock_handlers() -> tuple[MagicMock, MagicMock]:
    """
    Fixture that mocks FileHandler and StreamHandler used in the logger setup.

    :return: Tuple containing mocked file and stream handlers.
    """
    with patch("utils.logger.logging.FileHandler") as mock_file_handler, patch(
        "utils.logger.logging.StreamHandler"
    ) as mock_stream_handler, patch("utils.logger.LOG_TO_CONSOLE", True):
        mock_file = MagicMock()
        mock_stream = MagicMock()
        mock_file_handler.return_value = mock_file
        mock_stream_handler.return_value = mock_stream
        yield mock_file, mock_stream


@pytest.mark.unit
@pytest.mark.logger
def test_setup_logger_adds_handlers(mock_handlers: tuple[MagicMock, MagicMock]) -> None:
    """
    Test that setup_logger adds both FileHandler and StreamHandler with formatters.
    """
    mock_file, mock_stream = mock_handlers

    logger_name = "test_logger"
    log_level = logging.DEBUG
    filename = "test.log"

    logger = setup_logger(logger_name, log_level, filename)

    assert logger.name == logger_name
    assert logger.level == log_level
    assert any(
        isinstance(h, MagicMock) for h in logger.handlers
    ), "Logger has no handlers"
    assert mock_file.setFormatter.called, "FileHandler formatter not set"
    assert mock_stream.setFormatter.called, "StreamHandler formatter not set"


@pytest.mark.unit
@pytest.mark.logger
def test_setup_logger_without_console(monkeypatch) -> None:
    """
    Test that setup_logger skips StreamHandler when LOG_TO_CONSOLE is False.
    """
    monkeypatch.setattr("utils.logger.LOG_TO_CONSOLE", False)

    with patch("utils.logger.logging.FileHandler") as mock_file_handler, patch(
        "utils.logger.logging.StreamHandler"
    ) as mock_stream_handler:

        mock_file = MagicMock()
        mock_file_handler.return_value = mock_file

        logger = setup_logger("no_console_logger", logging.WARNING, "no_console.log")

        assert any(isinstance(h, MagicMock) for h in logger.handlers)
        assert mock_file.setFormatter.called
        mock_stream_handler.assert_not_called()


