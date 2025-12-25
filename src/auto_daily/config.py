"""Configuration module for auto-daily."""

import os
from pathlib import Path

import yaml
from dotenv import load_dotenv

ENV_LOG_DIR = "AUTO_DAILY_LOG_DIR"
DEFAULT_LOG_DIR = Path.home() / ".auto-daily" / "logs"
DEFAULT_REPORTS_DIR = Path.home() / ".auto-daily" / "reports"

# Ollama settings
DEFAULT_OLLAMA_BASE_URL = "http://localhost:11434"
DEFAULT_OLLAMA_MODEL = "llama3.2"
DEFAULT_CAPTURE_INTERVAL = 30

DEFAULT_PROMPT_TEMPLATE = """以下のアクティビティログに基づいて、日報を作成してください。

## 今日のアクティビティ
{activities}

## 日報フォーマット
以下の形式で日報を作成してください：

1. 今日の作業内容（箇条書き）
2. 進捗・成果
3. 課題・問題点
4. 明日の予定

日本語で簡潔に記述してください。"""


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


def get_prompt_template() -> str:
    """Get the prompt template for daily report generation.

    Reads from ~/.auto-daily/prompt.txt if it exists.
    Falls back to DEFAULT_PROMPT_TEMPLATE if not set.

    Returns:
        Prompt template string with {activities} placeholder.
    """
    prompt_file = Path.home() / ".auto-daily" / "prompt.txt"

    if prompt_file.exists():
        return prompt_file.read_text()

    return DEFAULT_PROMPT_TEMPLATE


def get_reports_dir() -> Path:
    """Get the reports directory path.

    Returns ~/.auto-daily/reports/.
    Creates the directory if it doesn't exist.

    Returns:
        Path to the reports directory.
    """
    reports_dir = DEFAULT_REPORTS_DIR
    reports_dir.mkdir(parents=True, exist_ok=True)
    return reports_dir


def get_slack_username(workspace: str) -> str | None:
    """Get the Slack username for a given workspace.

    Reads from ~/.auto-daily/slack_config.yaml if it exists.
    Returns None if the file doesn't exist or workspace is not found.

    Args:
        workspace: The Slack workspace name to look up.

    Returns:
        Username string if found, None otherwise.
    """
    config_file = Path.home() / ".auto-daily" / "slack_config.yaml"

    if not config_file.exists():
        return None

    config = yaml.safe_load(config_file.read_text())
    workspaces = config.get("workspaces", {})
    workspace_config = workspaces.get(workspace)

    if workspace_config is None:
        return None

    return workspace_config.get("username")


def load_env() -> None:
    """Load environment variables from .env file.

    Loads from ~/.auto-daily/.env if it exists.
    Does not override existing environment variables.
    """
    env_file = Path.home() / ".auto-daily" / ".env"
    load_dotenv(env_file)


def get_ollama_base_url() -> str:
    """Get the Ollama API base URL.

    Reads from OLLAMA_BASE_URL environment variable.
    Falls back to default (http://localhost:11434) if not set.

    Returns:
        Ollama API base URL.
    """
    return os.environ.get("OLLAMA_BASE_URL", DEFAULT_OLLAMA_BASE_URL)


def get_ollama_model() -> str:
    """Get the Ollama model name.

    Reads from OLLAMA_MODEL environment variable.
    Falls back to default (llama3.2) if not set.

    Returns:
        Ollama model name.
    """
    return os.environ.get("OLLAMA_MODEL", DEFAULT_OLLAMA_MODEL)


def get_capture_interval() -> int:
    """Get the capture interval in seconds.

    Reads from AUTO_DAILY_CAPTURE_INTERVAL environment variable.
    Falls back to default (30 seconds) if not set.

    Returns:
        Capture interval in seconds.
    """
    interval_str = os.environ.get("AUTO_DAILY_CAPTURE_INTERVAL")
    if interval_str is None:
        return DEFAULT_CAPTURE_INTERVAL
    return int(interval_str)
