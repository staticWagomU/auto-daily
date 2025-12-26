"""Shared pytest fixtures for auto_daily tests."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest


@pytest.fixture
def log_base(tmp_path: Path) -> Path:
    """Create a temporary log directory.

    This fixture creates a 'logs' subdirectory in pytest's tmp_path
    and returns its path. Use this for tests that need a log directory.

    Returns:
        Path to the temporary log directory.
    """
    log_dir = tmp_path / "logs"
    log_dir.mkdir()
    return log_dir


@pytest.fixture
def sample_window_info() -> dict[str, str]:
    """Provide sample window information for tests.

    Returns:
        Dictionary with app_name and window_title.
    """
    return {"app_name": "Test App", "window_title": "Test Window"}


@pytest.fixture(autouse=True)
def mock_ollama_connection():
    """Automatically mock check_ollama_connection to always return True.

    This prevents tests from failing when Ollama is not running.
    Tests that need to test connection failure can explicitly patch
    with return_value=False.
    """
    with patch("auto_daily.report.check_ollama_connection", return_value=True):
        yield
