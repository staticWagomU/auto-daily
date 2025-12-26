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

    When the config file is missing from both project root and home directory:
    1. Should not raise an error
    2. Should return None for any workspace
    """
    import os

    from auto_daily.config import get_slack_username

    # Arrange: Create empty project root (no slack_config.yaml)
    project_root = tmp_path / "project"
    project_root.mkdir()

    # Create home directory without slack_config.yaml
    home_dir = tmp_path / "home"
    config_dir = home_dir / ".auto-daily"
    config_dir.mkdir(parents=True)

    # Save current directory and change to project_root
    original_cwd = os.getcwd()
    try:
        os.chdir(project_root)

        # Mock Path.home() to return our simulated home directory
        with patch("auto_daily.config.Path.home", return_value=home_dir):
            # Act: Get username when neither file exists
            result = get_slack_username("Any Workspace")

            # Assert: Should return None
            assert result is None
    finally:
        # Restore original directory
        os.chdir(original_cwd)


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


# ============================================================
# PBI-019: プロジェクトルートの slack_config.yaml から読み込む
# ============================================================


def test_slack_config_from_project_root(tmp_path: Path) -> None:
    """Test that slack_config.yaml is loaded from project root first.

    The config should:
    1. Check for slack_config.yaml in the current working directory (project root)
    2. If exists, return the username from that file
    3. Take priority over ~/.auto-daily/slack_config.yaml
    """
    import os

    from auto_daily.config import get_slack_username

    # Arrange: Create slack_config.yaml in tmp_path (simulating project root)
    slack_config_file = tmp_path / "slack_config.yaml"
    slack_config_content = """workspaces:
  "Project Workspace":
    username: "project-user"
"""
    slack_config_file.write_text(slack_config_content)

    # Save current directory and change to tmp_path
    original_cwd = os.getcwd()
    try:
        os.chdir(tmp_path)

        # Act: Get username from project root config
        result = get_slack_username("Project Workspace")

        # Assert: Should return the project root username
        assert result == "project-user"
    finally:
        # Restore original directory
        os.chdir(original_cwd)


def test_slack_config_fallback_to_home(tmp_path: Path) -> None:
    """Test that slack_config.yaml falls back to home directory when not in project root.

    When slack_config.yaml is not found in project root, the config should:
    1. Fall back to ~/.auto-daily/slack_config.yaml
    2. Return the username from the home directory config
    """
    import os

    from auto_daily.config import get_slack_username

    # Arrange: Create empty project root (no slack_config.yaml)
    project_root = tmp_path / "project"
    project_root.mkdir()

    # Create slack_config.yaml in simulated home directory
    home_dir = tmp_path / "home"
    config_dir = home_dir / ".auto-daily"
    config_dir.mkdir(parents=True)
    slack_config_file = config_dir / "slack_config.yaml"
    slack_config_content = """workspaces:
  "Home Workspace":
    username: "home-user"
"""
    slack_config_file.write_text(slack_config_content)

    # Save current directory and change to project_root
    original_cwd = os.getcwd()
    try:
        os.chdir(project_root)

        # Mock Path.home() to return our simulated home directory
        with patch("auto_daily.config.Path.home", return_value=home_dir):
            # Act: Get username (should fall back to home directory)
            result = get_slack_username("Home Workspace")

            # Assert: Should return the home directory username
            assert result == "home-user"
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


# ============================================================
# PBI-021: LLM クライアント抽象化
# ============================================================


def test_ai_backend_from_env() -> None:
    """Test that AI_BACKEND environment variable sets the LLM backend.

    The config should:
    1. Read AI_BACKEND from environment
    2. Return the custom backend name when set
    3. Return "ollama" as default when not set
    """
    from auto_daily.config import get_ai_backend

    # Test custom backend
    with patch.dict(os.environ, {"AI_BACKEND": "lm_studio"}):
        result = get_ai_backend()
        assert result == "lm_studio"

    # Test default backend
    env_without_var = {k: v for k, v in os.environ.items() if k != "AI_BACKEND"}
    with patch.dict(os.environ, env_without_var, clear=True):
        result = get_ai_backend()
        assert result == "ollama"


# ============================================================
# PBI-028: OpenAI API 対応
# ============================================================


def test_openai_api_key_from_env() -> None:
    """Test that OPENAI_API_KEY environment variable sets the API key.

    The config should:
    1. Read OPENAI_API_KEY from environment
    2. Return the API key when set
    3. Return None when not set
    """
    from auto_daily.config import get_openai_api_key

    # Test with API key set
    with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test-key-12345"}):
        result = get_openai_api_key()
        assert result == "sk-test-key-12345"

    # Test without API key (should return None)
    env_without_var = {k: v for k, v in os.environ.items() if k != "OPENAI_API_KEY"}
    with patch.dict(os.environ, env_without_var, clear=True):
        result = get_openai_api_key()
        assert result is None


def test_openai_model_from_env() -> None:
    """Test that OPENAI_MODEL environment variable sets the model name.

    The config should:
    1. Read OPENAI_MODEL from environment
    2. Return the custom model name when set
    3. Return "gpt-4o-mini" as default when not set
    """
    from auto_daily.config import get_openai_model

    # Test with custom model
    with patch.dict(os.environ, {"OPENAI_MODEL": "gpt-4o"}):
        result = get_openai_model()
        assert result == "gpt-4o"

    # Test default model
    env_without_var = {k: v for k, v in os.environ.items() if k != "OPENAI_MODEL"}
    with patch.dict(os.environ, env_without_var, clear=True):
        result = get_openai_model()
        assert result == "gpt-4o-mini"


# ============================================================
# PBI-030: 日報保存先ディレクトリの設定
# ============================================================


def test_reports_dir_from_env(tmp_path: Path) -> None:
    """Test that AUTO_DAILY_REPORTS_DIR environment variable sets reports directory.

    The config should:
    1. Read AUTO_DAILY_REPORTS_DIR from environment
    2. Return that path as the reports directory
    3. Work with absolute paths
    """
    from auto_daily.config import get_reports_dir

    # Arrange: Set environment variable to custom directory
    custom_reports_dir = tmp_path / "custom_reports"
    custom_reports_dir.mkdir()

    # Clear project root influence by using tmp_path without reports/
    original_cwd = os.getcwd()
    try:
        os.chdir(tmp_path)

        with patch.dict(
            os.environ, {"AUTO_DAILY_REPORTS_DIR": str(custom_reports_dir)}
        ):
            # Act: Get reports directory
            result = get_reports_dir()

            # Assert: Should return the environment variable value
            assert result == custom_reports_dir
    finally:
        os.chdir(original_cwd)


def test_reports_dir_default(tmp_path: Path) -> None:
    """Test that default directory is used when env var is not set.

    When AUTO_DAILY_REPORTS_DIR is not set and no project reports/ exists,
    the config should:
    1. Return ~/.auto-daily/reports/ as the default
    2. Use the user's home directory
    """
    from auto_daily.config import get_reports_dir

    # Arrange: Create empty project root (no reports/ directory)
    project_root = tmp_path / "project"
    project_root.mkdir()

    # Ensure environment variable is NOT set
    env_without_var = {
        k: v for k, v in os.environ.items() if k != "AUTO_DAILY_REPORTS_DIR"
    }

    original_cwd = os.getcwd()
    try:
        os.chdir(project_root)

        with patch.dict(os.environ, env_without_var, clear=True):
            # Act: Get reports directory
            result = get_reports_dir()

            # Assert: Should return default path
            expected = Path.home() / ".auto-daily" / "reports"
            assert result == expected
    finally:
        os.chdir(original_cwd)


def test_reports_dir_auto_create(tmp_path: Path) -> None:
    """Test that reports directory is automatically created if it doesn't exist.

    The config should:
    1. Check if the directory exists
    2. Create it (including parents) if missing
    3. Return the path that now exists
    """
    from auto_daily.config import get_reports_dir

    # Arrange: Set environment variable to non-existent directory
    new_reports_dir = tmp_path / "new_reports" / "nested"
    assert not new_reports_dir.exists()

    # Create empty project root (no reports/ directory)
    project_root = tmp_path / "project"
    project_root.mkdir()

    original_cwd = os.getcwd()
    try:
        os.chdir(project_root)

        with patch.dict(os.environ, {"AUTO_DAILY_REPORTS_DIR": str(new_reports_dir)}):
            # Act: Get reports directory
            result = get_reports_dir()

            # Assert: Directory should now exist
            assert result == new_reports_dir
            assert new_reports_dir.exists()
            assert new_reports_dir.is_dir()
    finally:
        os.chdir(original_cwd)


def test_reports_dir_from_project_root(tmp_path: Path) -> None:
    """Test that project root reports/ directory is used when it exists.

    The config should:
    1. Check for reports/ directory in the current working directory
    2. If exists, return that path (highest priority)
    3. Take priority over AUTO_DAILY_REPORTS_DIR environment variable
    """
    from auto_daily.config import get_reports_dir

    # Arrange: Create reports/ directory in project root
    project_root = tmp_path / "project"
    project_root.mkdir()
    project_reports = project_root / "reports"
    project_reports.mkdir()

    # Also set environment variable (should be ignored due to project priority)
    env_reports_dir = tmp_path / "env_reports"
    env_reports_dir.mkdir()

    original_cwd = os.getcwd()
    try:
        os.chdir(project_root)

        with patch.dict(os.environ, {"AUTO_DAILY_REPORTS_DIR": str(env_reports_dir)}):
            # Act: Get reports directory
            result = get_reports_dir()

            # Assert: Should return project root reports/ (highest priority)
            assert result == project_reports
    finally:
        os.chdir(original_cwd)


# ============================================================
# PBI-022: LM Studio 対応
# ============================================================


def test_lm_studio_base_url_from_env() -> None:
    """Test that LM_STUDIO_BASE_URL environment variable sets the LM Studio URL.

    The config should:
    1. Read LM_STUDIO_BASE_URL from environment
    2. Return the custom URL when set
    3. Return "http://localhost:1234" as default when not set
    """
    from auto_daily.config import get_lm_studio_base_url

    # Test custom URL
    with patch.dict(os.environ, {"LM_STUDIO_BASE_URL": "http://custom:8080"}):
        result = get_lm_studio_base_url()
        assert result == "http://custom:8080"

    # Test default URL
    env_without_var = {k: v for k, v in os.environ.items() if k != "LM_STUDIO_BASE_URL"}
    with patch.dict(os.environ, env_without_var, clear=True):
        result = get_lm_studio_base_url()
        assert result == "http://localhost:1234"


# ============================================================
# PBI-023: OCR バックエンド抽象化
# ============================================================


def test_ocr_backend_from_env() -> None:
    """Test that OCR_BACKEND environment variable sets the OCR backend.

    The config should:
    1. Read OCR_BACKEND from environment
    2. Return the custom backend name when set
    3. Return "apple" as default when not set
    """
    from auto_daily.config import get_ocr_backend_name

    # Test custom backend
    with patch.dict(os.environ, {"OCR_BACKEND": "openai"}):
        result = get_ocr_backend_name()
        assert result == "openai"

    # Test default backend
    env_without_var = {k: v for k, v in os.environ.items() if k != "OCR_BACKEND"}
    with patch.dict(os.environ, env_without_var, clear=True):
        result = get_ocr_backend_name()
        assert result == "apple"


# ============================================================
# PBI-029: OpenAI Vision OCR
# ============================================================


def test_ocr_model_openai_from_env() -> None:
    """Test that OCR_MODEL environment variable sets the Vision model.

    The config should:
    1. Read OCR_MODEL from environment
    2. Return the custom model name when set
    3. Return "gpt-4o-mini" as default when not set
    """
    from auto_daily.config import get_ocr_model

    # Test custom model
    with patch.dict(os.environ, {"OCR_MODEL": "gpt-4o"}):
        result = get_ocr_model()
        assert result == "gpt-4o"

    # Test default model
    env_without_var = {k: v for k, v in os.environ.items() if k != "OCR_MODEL"}
    with patch.dict(os.environ, env_without_var, clear=True):
        result = get_ocr_model()
        assert result == "gpt-4o-mini"


# ============================================================
# PBI-024: Ollama Vision OCR
# ============================================================


def test_ocr_model_ollama_from_env() -> None:
    """Test that OCR_MODEL environment variable sets the Ollama Vision model.

    The config should:
    1. Allow setting OCR_MODEL to Ollama Vision models like "llava"
    2. OllamaVisionOCR should use this model
    """
    from auto_daily.ocr.ollama_vision import OllamaVisionOCR

    # Test with custom Ollama Vision model
    with patch.dict(os.environ, {"OCR_MODEL": "llava"}):
        backend = OllamaVisionOCR()
        assert backend.model == "llava"

    # Test with llama3.2-vision
    with patch.dict(os.environ, {"OCR_MODEL": "llama3.2-vision"}):
        backend = OllamaVisionOCR()
        assert backend.model == "llama3.2-vision"


# ============================================================
# PBI-035: 要約プロンプトのカスタマイズ
# ============================================================


def test_summary_prompt_template_from_file(tmp_path: Path) -> None:
    """Test that summary prompt template is loaded from summary_prompt.txt.

    The config should:
    1. Check for summary_prompt.txt in the current working directory
    2. If exists, return its content as the template
    3. Use Path.cwd() to find the file
    """
    from auto_daily.config import get_summary_prompt_template

    # Arrange: Create a custom summary_prompt.txt in tmp_path
    prompt_file = tmp_path / "summary_prompt.txt"
    custom_template = """カスタム要約プロンプトです。

## アクティビティログ
{log_content}

## 出力
- カスタム形式で要約してください
"""
    prompt_file.write_text(custom_template)

    # Save current directory and change to tmp_path
    original_cwd = os.getcwd()
    try:
        os.chdir(tmp_path)

        # Act: Get summary prompt template
        result = get_summary_prompt_template()

        # Assert: Should return the custom template
        assert result == custom_template
        assert "{log_content}" in result
        assert "カスタム" in result
    finally:
        # Restore original directory
        os.chdir(original_cwd)


def test_summary_prompt_template_default(tmp_path: Path) -> None:
    """Test that default template is used when summary_prompt.txt doesn't exist.

    When summary_prompt.txt doesn't exist in the current directory, the config should:
    1. Return the default summary prompt template
    2. Include {log_content} placeholder
    3. Include standard summary instructions
    """
    from auto_daily.config import (
        DEFAULT_SUMMARY_PROMPT_TEMPLATE,
        get_summary_prompt_template,
    )

    # Arrange: Use tmp_path as current working directory (no summary_prompt.txt)
    original_cwd = os.getcwd()
    try:
        os.chdir(tmp_path)

        # Act: Get summary prompt template
        result = get_summary_prompt_template()

        # Assert: Should return the default template
        assert result == DEFAULT_SUMMARY_PROMPT_TEMPLATE
        assert "{log_content}" in result
        assert "要約" in result
    finally:
        os.chdir(original_cwd)


# ============================================================
# PBI-038: OCR ノイズフィルタリング
# ============================================================


def test_ocr_filter_noise_from_env() -> None:
    """Test that OCR_FILTER_NOISE environment variable controls OCR filtering.

    The config should:
    1. Read OCR_FILTER_NOISE from environment
    2. Return True when set to "true" or "1" or not set (default)
    3. Return False when set to "false" or "0"
    """
    from auto_daily.config import get_ocr_filter_noise

    # Test default (should be True)
    env_without_var = {k: v for k, v in os.environ.items() if k != "OCR_FILTER_NOISE"}
    with patch.dict(os.environ, env_without_var, clear=True):
        result = get_ocr_filter_noise()
        assert result is True

    # Test explicit true values
    with patch.dict(os.environ, {"OCR_FILTER_NOISE": "true"}):
        result = get_ocr_filter_noise()
        assert result is True

    with patch.dict(os.environ, {"OCR_FILTER_NOISE": "1"}):
        result = get_ocr_filter_noise()
        assert result is True

    # Test false values
    with patch.dict(os.environ, {"OCR_FILTER_NOISE": "false"}):
        result = get_ocr_filter_noise()
        assert result is False

    with patch.dict(os.environ, {"OCR_FILTER_NOISE": "0"}):
        result = get_ocr_filter_noise()
        assert result is False
