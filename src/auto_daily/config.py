"""Configuration module for auto-daily."""

import os
from pathlib import Path

import yaml
from dotenv import load_dotenv

ENV_LOG_DIR = "AUTO_DAILY_LOG_DIR"
DEFAULT_LOG_DIR = Path.home() / ".auto-daily" / "logs"
DEFAULT_REPORTS_DIR = Path.home() / ".auto-daily" / "reports"
DEFAULT_SUMMARIES_DIR = Path.home() / ".auto-daily" / "summaries"

# Ollama settings
DEFAULT_OLLAMA_BASE_URL = "http://localhost:11434"
DEFAULT_OLLAMA_MODEL = "llama3.2"
DEFAULT_CAPTURE_INTERVAL = 30

# LLM backend settings
DEFAULT_AI_BACKEND = "ollama"

# OpenAI settings
DEFAULT_OPENAI_MODEL = "gpt-4o-mini"

# LM Studio settings
DEFAULT_LM_STUDIO_BASE_URL = "http://localhost:1234"
DEFAULT_LM_STUDIO_MODEL = "default"

# OCR settings
DEFAULT_OCR_BACKEND = "apple"
DEFAULT_OCR_MODEL = "gpt-4o-mini"
DEFAULT_OCR_FILTER_NOISE = True

# Summary prompt template
DEFAULT_SUMMARY_PROMPT_TEMPLATE = """以下の1時間分のアクティビティログを、精度重視で要約してください。

## ガイドライン（重要）
- 具体的な成果物を抽出する（ファイル名、関数名、クラス名、コマンド、チケットID、会議名、URL）
- 同一アプリで連続する操作はまとめ、目的→実施→結果で表現する
- OCR テキストから文脈を補完するが、推測は断定せず「推測」表記にする
- Slack は「誰と」「何について」「結論/宿題」を明記する
- 無意味な断片、UI要素、通知、短いゴミ文字列は除外する

## 除外対象
- システム通知、メニューバー、ボタン名のみの文字列
- パスワード/トークンと思われる文字列
- 連続記号や意味のない短文

## アクティビティログ
{log_content}

## 出力フォーマット
### 主な作業
- [成果物/タスク名]: [目的] → [実施] → [結果]（根拠: [ファイル/関数/コマンド等]）

### コミュニケーション
- [相手/チャンネル]: [話題] / [結論・宿題]

### 使用ツール
[アプリ名のリスト]"""

DEFAULT_PROMPT_TEMPLATE = """以下のアクティビティログに基づいて、日報を作成してください。
可能な限り具体的に、成果物（ファイル名・関数名・変更内容・チケットID・会議名など）を記載してください。
不確実な推測は「不明」または「要確認」と明記し、断定しないでください。

## 日報の作成ルール
- 具体名を優先: ファイル/関数/クラス/コマンド/議題/URL/PR/Issue など
- 冗長な重複を統合し、時系列より成果ベースで整理
- OCR ノイズっぽい断片（短い文字列やUI要素）は除外
- 目的/背景 → 実施 → 結果の順で書く

## 今日のアクティビティ
{activities}

## 出力フォーマット
### 1. 今日の作業内容（箇条書き）
- [成果物/タスク名]: [目的/背景] → [実施内容] → [結果]

### 2. 進捗・成果
- [具体的な進捗]: [根拠となるログ/成果物]

### 3. 課題・問題点
- [課題]: [状況/影響/次の一手]

### 4. コミュニケーション（あれば）
- [相手/チャンネル]: [話題/決定事項]

### 5. 次アクション（あれば）
- [項目]: [次の作業]
"""


def get_log_dir() -> Path:
    """Get the log directory path.

    Reads from AUTO_DAILY_LOG_DIR environment variable.
    Falls back to ~/.auto-daily/logs/ if not set.
    Creates the directory if it doesn't exist.

    Returns:
        Path to the log directory.
    """
    env_value = os.environ.get(ENV_LOG_DIR)
    if env_value:
        # Expand ~ to home directory
        log_dir = Path(os.path.expanduser(env_value))
    else:
        log_dir = DEFAULT_LOG_DIR

    log_dir.mkdir(parents=True, exist_ok=True)

    return log_dir


def get_prompt_template() -> str:
    """Get the prompt template for daily report generation.

    Reads from prompt.txt in the current working directory (project root).
    Falls back to DEFAULT_PROMPT_TEMPLATE if not found.

    Returns:
        Prompt template string with {activities} placeholder.
    """
    prompt_file = Path.cwd() / "prompt.txt"

    if prompt_file.exists():
        return prompt_file.read_text()

    return DEFAULT_PROMPT_TEMPLATE


def get_reports_dir() -> Path:
    """Get the reports directory path.

    Priority order:
    1. Project root's reports/ directory (if exists)
    2. AUTO_DAILY_REPORTS_DIR environment variable
    3. Default: ~/.auto-daily/reports/

    Creates the directory if it doesn't exist (except for project root).

    Returns:
        Path to the reports directory.
    """
    # 1. Check for project root reports/ directory
    project_reports = Path.cwd() / "reports"
    if project_reports.exists() and project_reports.is_dir():
        return project_reports

    # 2. Check environment variable
    env_value = os.environ.get("AUTO_DAILY_REPORTS_DIR")
    if env_value:
        # Expand ~ to home directory
        reports_dir = Path(os.path.expanduser(env_value))
        reports_dir.mkdir(parents=True, exist_ok=True)
        return reports_dir

    # 3. Use default
    reports_dir = DEFAULT_REPORTS_DIR
    reports_dir.mkdir(parents=True, exist_ok=True)
    return reports_dir


def get_slack_username(workspace: str) -> str | None:
    """Get the Slack username for a given workspace.

    Reads from slack_config.yaml in the following order:
    1. Current working directory (project root) - slack_config.yaml
    2. Home directory - ~/.auto-daily/slack_config.yaml

    Returns None if neither file exists or workspace is not found.

    Args:
        workspace: The Slack workspace name to look up.

    Returns:
        Username string if found, None otherwise.
    """
    # 1. Check project root first
    project_config = Path.cwd() / "slack_config.yaml"
    if project_config.exists():
        config = yaml.safe_load(project_config.read_text())
        workspaces = config.get("workspaces", {})
        workspace_config = workspaces.get(workspace)
        if workspace_config is not None:
            return workspace_config.get("username")

    # 2. Fall back to home directory
    home_config = Path.home() / ".auto-daily" / "slack_config.yaml"
    if home_config.exists():
        config = yaml.safe_load(home_config.read_text())
        workspaces = config.get("workspaces", {})
        workspace_config = workspaces.get(workspace)
        if workspace_config is not None:
            return workspace_config.get("username")

    return None


def load_env() -> None:
    """Load environment variables from .env file.

    Loads from project root .env if it exists.
    Does not override existing environment variables.
    """
    # Load from project root (where pyproject.toml is located)
    load_dotenv()


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


def get_ai_backend() -> str:
    """Get the AI backend to use.

    Reads from AI_BACKEND environment variable.
    Falls back to default ("ollama") if not set.

    Returns:
        AI backend name ("ollama", "openai", etc.).
    """
    return os.environ.get("AI_BACKEND", DEFAULT_AI_BACKEND)


def get_openai_api_key() -> str | None:
    """Get the OpenAI API key.

    Reads from OPENAI_API_KEY environment variable.

    Returns:
        OpenAI API key if set, None otherwise.
    """
    return os.environ.get("OPENAI_API_KEY")


def get_openai_model() -> str:
    """Get the OpenAI model name.

    Reads from OPENAI_MODEL environment variable.
    Falls back to default (gpt-4o-mini) if not set.

    Returns:
        OpenAI model name.
    """
    return os.environ.get("OPENAI_MODEL", DEFAULT_OPENAI_MODEL)


def get_lm_studio_base_url() -> str:
    """Get the LM Studio API base URL.

    Reads from LM_STUDIO_BASE_URL environment variable.
    Falls back to default (http://localhost:1234) if not set.

    Returns:
        LM Studio API base URL.
    """
    return os.environ.get("LM_STUDIO_BASE_URL", DEFAULT_LM_STUDIO_BASE_URL)


def get_lm_studio_model() -> str:
    """Get the LM Studio model name.

    Reads from LM_STUDIO_MODEL environment variable.
    Falls back to default ("default") if not set.

    Returns:
        LM Studio model name.
    """
    return os.environ.get("LM_STUDIO_MODEL", DEFAULT_LM_STUDIO_MODEL)


def get_ocr_backend_name() -> str:
    """Get the OCR backend name.

    Reads from OCR_BACKEND environment variable.
    Falls back to default ("apple") if not set.

    Returns:
        OCR backend name ("apple", "openai", etc.).
    """
    return os.environ.get("OCR_BACKEND", DEFAULT_OCR_BACKEND)


def get_ocr_model() -> str:
    """Get the OCR model name for Vision API.

    Reads from OCR_MODEL environment variable.
    Falls back to default ("gpt-4o-mini") if not set.

    Returns:
        OCR model name for Vision API.
    """
    return os.environ.get("OCR_MODEL", DEFAULT_OCR_MODEL)


def get_summaries_dir() -> Path:
    """Get the summaries directory path.

    Reads from AUTO_DAILY_SUMMARIES_DIR environment variable.
    Falls back to ~/.auto-daily/summaries/ if not set.
    Creates the directory if it doesn't exist.

    Returns:
        Path to the summaries directory.
    """
    env_value = os.environ.get("AUTO_DAILY_SUMMARIES_DIR")
    if env_value:
        # Expand ~ to home directory
        summaries_dir = Path(os.path.expanduser(env_value))
    else:
        summaries_dir = DEFAULT_SUMMARIES_DIR

    summaries_dir.mkdir(parents=True, exist_ok=True)

    return summaries_dir


def get_summary_prompt_template() -> str:
    """Get the prompt template for hourly summarization.

    Reads from summary_prompt.txt in the current working directory.
    Falls back to DEFAULT_SUMMARY_PROMPT_TEMPLATE if not found.

    Returns:
        Prompt template string with {log_content} placeholder.
    """
    prompt_file = Path.cwd() / "summary_prompt.txt"

    if prompt_file.exists():
        return prompt_file.read_text()

    return DEFAULT_SUMMARY_PROMPT_TEMPLATE


def get_ocr_filter_noise() -> bool:
    """Get whether OCR noise filtering is enabled.

    Reads from OCR_FILTER_NOISE environment variable.
    Falls back to True (enabled) if not set.

    Accepts:
    - "true" or "1" for enabled
    - "false" or "0" for disabled

    Returns:
        True if noise filtering is enabled, False otherwise.
    """
    value = os.environ.get("OCR_FILTER_NOISE")

    if value is None:
        return DEFAULT_OCR_FILTER_NOISE

    return value.lower() in ("true", "1")
