"""Tests for Ollama API integration."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from auto_daily.ollama import OllamaClient


@pytest.mark.asyncio
async def test_scheduled_call() -> None:
    """Test that OllamaClient can call the Ollama API.

    The function should:
    1. Send a request to the Ollama API endpoint
    2. Return the generated response text
    3. Handle connection errors gracefully
    """
    # Arrange
    client = OllamaClient(base_url="http://localhost:11434")
    mock_response_data = {"response": "This is a test response from Ollama."}

    # Create a mock response object
    mock_response = MagicMock()
    mock_response.json.return_value = mock_response_data
    mock_response.raise_for_status = MagicMock()

    # Mock the AsyncClient context manager and post method
    mock_post = AsyncMock(return_value=mock_response)

    with patch("auto_daily.ollama.httpx.AsyncClient") as mock_client_class:
        mock_client_instance = AsyncMock()
        mock_client_instance.post = mock_post
        mock_client_instance.__aenter__.return_value = mock_client_instance
        mock_client_instance.__aexit__.return_value = None
        mock_client_class.return_value = mock_client_instance

        # Act
        result = await client.generate(
            model="llama3.2",
            prompt="Hello, this is a test.",
        )

        # Assert
        assert result == "This is a test response from Ollama."
        mock_post.assert_called_once()


def test_prompt_generation(tmp_path) -> None:
    """Test that generate_daily_report_prompt creates a proper prompt from logs.

    The function should:
    1. Read JSONL log file
    2. Extract activity entries
    3. Format them into a prompt for daily report generation
    """
    import json

    from auto_daily.ollama import generate_daily_report_prompt

    # Arrange: Create a sample JSONL log file
    log_file = tmp_path / "activity_2024-12-25.jsonl"
    entries = [
        {
            "timestamp": "2024-12-25T09:00:00",
            "window_info": {"app_name": "VSCode", "window_title": "main.py"},
            "ocr_text": "def hello_world():",
        },
        {
            "timestamp": "2024-12-25T10:00:00",
            "window_info": {"app_name": "Chrome", "window_title": "GitHub"},
            "ocr_text": "Pull Request #123",
        },
        {
            "timestamp": "2024-12-25T11:00:00",
            "window_info": {"app_name": "Slack", "window_title": "#general"},
            "ocr_text": "Meeting at 2pm",
        },
    ]

    with open(log_file, "w") as f:
        for entry in entries:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    # Act
    prompt = generate_daily_report_prompt(log_file)

    # Assert
    assert isinstance(prompt, str)
    assert len(prompt) > 0
    # Check that the prompt contains activity information
    assert "VSCode" in prompt
    assert "Chrome" in prompt
    assert "Slack" in prompt
    # Check that it includes instructions for generating a report
    assert "日報" in prompt or "daily report" in prompt.lower()


def test_save_daily_report(tmp_path) -> None:
    """Test that save_daily_report saves the generated report to a file.

    The function should:
    1. Create the output directory if it doesn't exist
    2. Save the report as a Markdown file with date-based filename
    3. Write the provided content to the file
    """
    from datetime import date

    from auto_daily.ollama import save_daily_report

    # Arrange
    output_dir = tmp_path / "reports"
    report_content = """# 日報 2024-12-25

## 今日の作業内容
- VSCode でコードの実装
- GitHub で PR のレビュー
- Slack でミーティングの調整

## 進捗・成果
- 機能実装が完了

## 課題・問題点
- なし

## 明日の予定
- テストの追加
"""
    report_date = date(2024, 12, 25)

    # Act
    result_path = save_daily_report(output_dir, report_content, report_date)

    # Assert
    # The output directory should be created
    assert output_dir.exists()
    assert output_dir.is_dir()

    # The file should be created with the correct name
    expected_filename = "daily_report_2024-12-25.md"
    expected_path = output_dir / expected_filename
    assert result_path == expected_path
    assert expected_path.exists()

    # The content should match
    saved_content = expected_path.read_text()
    assert saved_content == report_content
