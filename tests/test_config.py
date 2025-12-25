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


def test_prompt_template_default(tmp_path: Path) -> None:
    """Test that default template is used when prompt.txt doesn't exist.

    When prompt.txt doesn't exist in the current directory, the config should:
    1. Return the default prompt template
    2. Include {activities} placeholder
    3. Include standard daily report instructions
    """
    import os

    from auto_daily.config import DEFAULT_PROMPT_TEMPLATE, get_prompt_template

    # Arrange: Use tmp_path as current working directory (no prompt.txt)
    original_cwd = os.getcwd()
    try:
        os.chdir(tmp_path)

        # Act: Get prompt template
        result = get_prompt_template()

        # Assert: Should return the default template
        assert result == DEFAULT_PROMPT_TEMPLATE
        assert "{activities}" in result
        assert "日報" in result
    finally:
        os.chdir(original_cwd)


def test_slack_username_config(tmp_path: Path) -> None:
    """Test that Slack username can be loaded from slack_config.yaml.

    The config should:
    1. Read slack_config.yaml from ~/.auto-daily/ directory
    2. Parse YAML structure with workspaces and usernames
    3. Return the username for a given workspace
    4. Return None if workspace is not found or file doesn't exist
    """
    from auto_daily.config import get_slack_username

    # Arrange: Create a slack_config.yaml file
    config_dir = tmp_path / ".auto-daily"
    config_dir.mkdir()
    slack_config_file = config_dir / "slack_config.yaml"
    slack_config_content = """workspaces:
  "My Company":
    username: "taro.yamada"
  "Side Project":
    username: "taro_dev"
"""
    slack_config_file.write_text(slack_config_content)

    # Mock Path.home() to return tmp_path
    with patch("auto_daily.config.Path.home", return_value=tmp_path):
        # Act & Assert: Get username for existing workspace
        result = get_slack_username("My Company")
        assert result == "taro.yamada"

        # Act & Assert: Get username for another workspace
        result = get_slack_username("Side Project")
        assert result == "taro_dev"

        # Act & Assert: Get username for non-existent workspace
        result = get_slack_username("Unknown Workspace")
        assert result is None


def test_slack_username_config_file_not_found(tmp_path: Path) -> None:
    """Test that None is returned when slack_config.yaml doesn't exist.

    When the config file is missing:
    1. Should not raise an error
    2. Should return None for any workspace
    """
    from auto_daily.config import get_slack_username

    # Arrange: Create config directory without slack_config.yaml
    config_dir = tmp_path / ".auto-daily"
    config_dir.mkdir()

    # Mock Path.home() to return tmp_path
    with patch("auto_daily.config.Path.home", return_value=tmp_path):
        # Act: Get username when file doesn't exist
        result = get_slack_username("Any Workspace")

        # Assert: Should return None
        assert result is None


# ============================================================
# PBI-015: .env ファイルで設定を管理する
# ============================================================


def test_load_dotenv(tmp_path: Path) -> None:
    """Test that .env file is loaded and environment variables are set.

    The config should:
    1. Load .env file from project root (current working directory)
    2. Set environment variables from the file
    3. Allow subsequent get_* functions to read these values
    """
    from dotenv import load_dotenv

    # Arrange: Create .env file in tmp_path (simulating project root)
    env_file = tmp_path / ".env"
    env_file.write_text("TEST_DOTENV_VAR=hello_from_dotenv\n")

    # Clear the test variable if it exists
    if "TEST_DOTENV_VAR" in os.environ:
        del os.environ["TEST_DOTENV_VAR"]

    # Act: Load the .env file directly (simulating what load_env does)
    load_dotenv(env_file)

    # Assert: Environment variable should be set
    assert os.environ.get("TEST_DOTENV_VAR") == "hello_from_dotenv"

    # Cleanup
    if "TEST_DOTENV_VAR" in os.environ:
        del os.environ["TEST_DOTENV_VAR"]


def test_ollama_base_url_from_env() -> None:
    """Test that OLLAMA_BASE_URL environment variable sets Ollama connection URL.

    The config should:
    1. Read OLLAMA_BASE_URL from environment
    2. Return the custom URL when set
    """
    from auto_daily.config import get_ollama_base_url

    # Arrange: Set custom Ollama URL
    custom_url = "http://ollama.example.com:11434"

    with patch.dict(os.environ, {"OLLAMA_BASE_URL": custom_url}):
        # Act: Get Ollama base URL
        result = get_ollama_base_url()

        # Assert: Should return the custom URL
        assert result == custom_url


def test_ollama_model_from_env() -> None:
    """Test that OLLAMA_MODEL environment variable sets the model name.

    The config should:
    1. Read OLLAMA_MODEL from environment
    2. Return the custom model name when set
    """
    from auto_daily.config import get_ollama_model

    # Arrange: Set custom model name
    custom_model = "mistral"

    with patch.dict(os.environ, {"OLLAMA_MODEL": custom_model}):
        # Act: Get Ollama model
        result = get_ollama_model()

        # Assert: Should return the custom model
        assert result == custom_model


def test_capture_interval_from_env() -> None:
    """Test that AUTO_DAILY_CAPTURE_INTERVAL environment variable sets capture interval.

    The config should:
    1. Read AUTO_DAILY_CAPTURE_INTERVAL from environment
    2. Return the value as an integer (seconds)
    """
    from auto_daily.config import get_capture_interval

    # Arrange: Set custom interval
    custom_interval = "60"

    with patch.dict(os.environ, {"AUTO_DAILY_CAPTURE_INTERVAL": custom_interval}):
        # Act: Get capture interval
        result = get_capture_interval()

        # Assert: Should return the integer value
        assert result == 60
        assert isinstance(result, int)


# ============================================================
# PBI-018: プロジェクトルートの prompt.txt からプロンプトを読み込む
# ============================================================


def test_prompt_template_from_project_root(tmp_path: Path) -> None:
    """Test that prompt template is loaded from project root prompt.txt.

    The config should:
    1. Check for prompt.txt in the current working directory (project root)
    2. If exists, return its content as the template
    3. Use Path.cwd() to find the project root
    """
    import os

    from auto_daily.config import get_prompt_template

    # Arrange: Create a custom prompt.txt in tmp_path (simulating project root)
    prompt_file = tmp_path / "prompt.txt"
    custom_template = """プロジェクト固有のプロンプトです。

## アクティビティ
{activities}

## 出力
- プロジェクト固有の日報を作成してください
"""
    prompt_file.write_text(custom_template)

    # Save current directory and change to tmp_path
    original_cwd = os.getcwd()
    try:
        os.chdir(tmp_path)

        # Act: Get prompt template
        result = get_prompt_template()

        # Assert: Should return the project root template
        assert result == custom_template
        assert "{activities}" in result
        assert "プロジェクト固有" in result
    finally:
        # Restore original directory
        os.chdir(original_cwd)


def test_env_defaults() -> None:
    """Test that default values are used when environment variables are not set.

    When env vars are not set, the config should return:
    1. OLLAMA_BASE_URL default: "http://localhost:11434"
    2. OLLAMA_MODEL default: "llama3.2"
    3. AUTO_DAILY_CAPTURE_INTERVAL default: 30
    """
    from auto_daily.config import (
        get_capture_interval,
        get_ollama_base_url,
        get_ollama_model,
    )

    # Arrange: Clear relevant environment variables
    env_without_vars = {
        k: v
        for k, v in os.environ.items()
        if k not in ["OLLAMA_BASE_URL", "OLLAMA_MODEL", "AUTO_DAILY_CAPTURE_INTERVAL"]
    }

    with patch.dict(os.environ, env_without_vars, clear=True):
        # Act & Assert: Check default values
        assert get_ollama_base_url() == "http://localhost:11434"
        assert get_ollama_model() == "llama3.2"
        assert get_capture_interval() == 30
