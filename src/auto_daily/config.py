"""Configuration module for auto-daily."""

import os
from pathlib import Path

ENV_LOG_DIR = "AUTO_DAILY_LOG_DIR"
DEFAULT_LOG_DIR = Path.home() / ".auto-daily" / "logs"


def get_log_dir() -> Path:
    """Get the log directory path.

    Reads from AUTO_DAILY_LOG_DIR environment variable.
    Falls back to ~/.auto-daily/logs/ if not set.
    Creates the directory if it doesn't exist.

    Returns:
        Path to the log directory.
    """
    env_value = os.environ.get(ENV_LOG_DIR)
    log_dir = Path(env_value) if env_value else DEFAULT_LOG_DIR

    log_dir.mkdir(parents=True, exist_ok=True)

    return log_dir
