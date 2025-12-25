"""Tests for summarize command (PBI-026)."""

import json
from datetime import date, datetime
from unittest.mock import AsyncMock, patch


def test_summarize_command(tmp_path, monkeypatch) -> None:
    """Test that 'python -m auto_daily summarize' generates an hourly summary.

    The summarize command should:
    1. Read the current hour's log file from the log directory
    2. Generate a summary using Ollama
    3. Save the summary to summaries/YYYY-MM-DD/summary_HH.md
    """
    import auto_daily
    from auto_daily.logger import get_log_dir_for_date, get_log_filename

    # Arrange: Create a temporary log directory with an hourly log file
    log_dir = tmp_path / "logs"
    log_dir.mkdir()
    summaries_dir = tmp_path / "summaries"

    # Create a log file for the current hour
    now = datetime.now()
    date_log_dir = get_log_dir_for_date(log_dir, now)
    log_file = date_log_dir / get_log_filename(now)
    log_entry = {
        "timestamp": now.isoformat(),
        "window_info": {"app_name": "Code", "window_title": "test.py"},
        "ocr_text": "Implementing new feature",
    }
    log_file.write_text(json.dumps(log_entry) + "\n")

    # Mock environment and Ollama
    monkeypatch.setenv("AUTO_DAILY_LOG_DIR", str(log_dir))
    monkeypatch.setenv("AUTO_DAILY_SUMMARIES_DIR", str(summaries_dir))

    mock_client = AsyncMock()
    mock_client.generate.return_value = "- 新機能の実装を行った"

    with (
        patch.object(auto_daily, "OllamaClient", return_value=mock_client),
        patch("sys.argv", ["auto-daily", "summarize"]),
    ):
        # Act: Call main with summarize command
        auto_daily.main()

    # Assert: Summary file should be created
    summary_date_dir = summaries_dir / now.strftime("%Y-%m-%d")
    summary_file = summary_date_dir / f"summary_{now.strftime('%H')}.md"
    assert summary_file.exists()
    assert "新機能の実装" in summary_file.read_text()


def test_summary_date_directory(tmp_path) -> None:
    """Test that summaries/YYYY-MM-DD/ directory is automatically created.

    The get_summary_dir_for_date function should:
    1. Return a Path to summaries/YYYY-MM-DD/
    2. Create the directory if it doesn't exist
    3. Use the provided date for the directory name
    """
    from auto_daily.summarize import get_summary_dir_for_date

    # Arrange
    summaries_base = tmp_path / "summaries"
    target_date = date(2025, 12, 25)

    # Act
    result = get_summary_dir_for_date(summaries_base, target_date)

    # Assert
    assert result == summaries_base / "2025-12-25"
    assert result.exists()
    assert result.is_dir()


def test_summary_file_format(tmp_path) -> None:
    """Test that summary is saved as summary_HH.md format.

    The save_summary function should:
    1. Save the summary to summaries/YYYY-MM-DD/summary_HH.md
    2. Use zero-padded hour (e.g., summary_09.md)
    3. Create the date directory if needed
    """
    from auto_daily.summarize import get_summary_filename, save_summary

    # Test get_summary_filename
    assert get_summary_filename(9) == "summary_09.md"
    assert get_summary_filename(14) == "summary_14.md"
    assert get_summary_filename(0) == "summary_00.md"
    assert get_summary_filename(23) == "summary_23.md"

    # Test save_summary
    summaries_base = tmp_path / "summaries"
    target_date = date(2025, 12, 25)
    hour = 14
    content = "# 14:00-15:00 の要約\n\n- タスクAを完了\n- ミーティング参加"

    save_summary(summaries_base, target_date, hour, content)

    # Assert
    summary_file = summaries_base / "2025-12-25" / "summary_14.md"
    assert summary_file.exists()
    assert summary_file.read_text() == content
