"""Tests for configuration module."""

import os
from pathlib import Path
from unittest.mock import patch


def test_log_dir_from_env(tmp_path: Path) -> None:
    """Test that AUTO_DAILY_LOG_DIR environment variable sets log directory.

    The config should:
    1. Read AUTO_DAILY_LOG_DIR from environment
    2. Return that path as the log directory
    3. Work with absolute paths
    """
    from auto_daily.config import get_log_dir

    # Arrange: Set environment variable to custom directory
    custom_log_dir = tmp_path / "custom_logs"
    custom_log_dir.mkdir()

    with patch.dict(os.environ, {"AUTO_DAILY_LOG_DIR": str(custom_log_dir)}):
        # Act: Get log directory
        result = get_log_dir()

        # Assert: Should return the environment variable value
        assert result == custom_log_dir


def test_log_dir_default() -> None:
    """Test that default directory is used when env var is not set.

    When AUTO_DAILY_LOG_DIR is not set, the config should:
    1. Return ~/.auto-daily/logs/ as the default
    2. Use the user's home directory
    """
    from auto_daily.config import get_log_dir

    # Arrange: Ensure environment variable is NOT set
    env_without_var = {k: v for k, v in os.environ.items() if k != "AUTO_DAILY_LOG_DIR"}

    with patch.dict(os.environ, env_without_var, clear=True):
        # Act: Get log directory
        result = get_log_dir()

        # Assert: Should return default path
        expected = Path.home() / ".auto-daily" / "logs"
        assert result == expected


def test_log_dir_auto_create(tmp_path: Path) -> None:
    """Test that log directory is automatically created if it doesn't exist.

    The config should:
    1. Check if the directory exists
    2. Create it (including parents) if missing
    3. Return the path that now exists
    """
    from auto_daily.config import get_log_dir

    # Arrange: Set environment variable to non-existent directory
    new_log_dir = tmp_path / "new_logs" / "nested"
    assert not new_log_dir.exists()

    with patch.dict(os.environ, {"AUTO_DAILY_LOG_DIR": str(new_log_dir)}):
        # Act: Get log directory
        result = get_log_dir()

        # Assert: Directory should now exist
        assert result == new_log_dir
        assert new_log_dir.exists()
        assert new_log_dir.is_dir()


def test_prompt_template_from_file(tmp_path: Path) -> None:
    """Test that prompt template is loaded from ~/.auto-daily/prompt.txt.

    The config should:
    1. Read prompt template from the specified file path
    2. Return the file content as the template string
    3. Support custom prompts defined by the user
    """
    from auto_daily.config import get_prompt_template

    # Arrange: Create a custom prompt template file
    config_dir = tmp_path / ".auto-daily"
    config_dir.mkdir()
    prompt_file = config_dir / "prompt.txt"
    custom_template = """カスタムプロンプトテンプレートです。

## アクティビティ
{activities}

## 出力形式
- 作業内容を要約してください
"""
    prompt_file.write_text(custom_template)

    # Mock Path.home() to return tmp_path
    with patch("auto_daily.config.Path.home", return_value=tmp_path):
        # Act: Get prompt template
        result = get_prompt_template()

        # Assert: Should return the custom template content
        assert result == custom_template
        assert "{activities}" in result


def test_prompt_template_default(tmp_path: Path) -> None:
    """Test that default template is used when prompt.txt doesn't exist.

    When ~/.auto-daily/prompt.txt doesn't exist, the config should:
    1. Return the default prompt template
    2. Include {activities} placeholder
    3. Include standard daily report instructions
    """
    from auto_daily.config import DEFAULT_PROMPT_TEMPLATE, get_prompt_template

    # Arrange: Ensure no prompt.txt exists (use tmp_path as home)
    config_dir = tmp_path / ".auto-daily"
    config_dir.mkdir()  # Create the directory but not the prompt.txt file

    # Mock Path.home() to return tmp_path
    with patch("auto_daily.config.Path.home", return_value=tmp_path):
        # Act: Get prompt template
        result = get_prompt_template()

        # Assert: Should return the default template
        assert result == DEFAULT_PROMPT_TEMPLATE
        assert "{activities}" in result
        assert "日報" in result
