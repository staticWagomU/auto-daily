"""Configuration module for auto-daily."""

import os
from pathlib import Path

import yaml

ENV_LOG_DIR = "AUTO_DAILY_LOG_DIR"
DEFAULT_LOG_DIR = Path.home() / ".auto-daily" / "logs"

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
