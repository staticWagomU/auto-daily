"""Tests for main entrypoint."""

import subprocess
import sys


def test_module_execution() -> None:
    """Test that python -m auto_daily runs successfully.

    The module should:
    1. Be executable via python -m auto_daily
    2. Exit with code 0 on normal termination
    3. Import and call the main() function
    """
    # Act: Run the module with --help or a quick exit flag
    # We use a timeout to avoid hanging if the app starts monitoring
    result = subprocess.run(
        [sys.executable, "-m", "auto_daily", "--help"],
        capture_output=True,
        text=True,
        timeout=5,
    )

    # Assert: Should exit cleanly (0) or show help/usage
    # --help typically exits with 0
    assert result.returncode == 0
    assert "auto-daily" in result.stdout.lower() or "usage" in result.stdout.lower()


def test_cli_entrypoint() -> None:
    """Test that auto-daily command works via pyproject.toml scripts.

    The CLI should:
    1. Be callable via the 'auto-daily' command after pip install
    2. Support --help flag
    3. Show usage information
    """
    # Act: Import and call main directly (simulates CLI invocation)
    from auto_daily import main

    # Verify main is callable
    assert callable(main)

    # Test via subprocess with the scripts entry point
    # This requires the package to be installed in editable mode
    result = subprocess.run(
        [sys.executable, "-c", "from auto_daily import main; main()"],
        input="",
        capture_output=True,
        text=True,
        timeout=5,
        env={**dict(__import__("os").environ), "COLUMNS": "80"},
    )

    # When called without args, should print version and exit normally
    assert result.returncode == 0
    assert "auto-daily" in result.stdout.lower()


def test_main_starts_monitoring() -> None:
    """Test that main() starts the window monitoring loop when --start is passed.

    The main function should:
    1. Accept a --start flag to begin monitoring
    2. Create a WindowMonitor instance
    3. Call WindowMonitor.start() to begin the monitoring loop
    """
    from unittest.mock import MagicMock, patch

    # Arrange: Mock WindowMonitor to avoid actual monitoring
    mock_monitor_instance = MagicMock()
    mock_monitor_class = MagicMock(return_value=mock_monitor_instance)

    with (
        patch("auto_daily.WindowMonitor", mock_monitor_class),
        patch("sys.argv", ["auto-daily", "--start"]),
        patch("time.sleep", side_effect=KeyboardInterrupt),  # Stop loop immediately
    ):
        from auto_daily import main

        # Act: Call main with --start
        try:
            main()
        except (KeyboardInterrupt, SystemExit):
            pass  # Expected when we interrupt the loop

    # Assert: WindowMonitor should have been instantiated and started
    mock_monitor_class.assert_called_once()
    mock_monitor_instance.start.assert_called_once()


def test_report_command(tmp_path, monkeypatch) -> None:
    """Test that 'python -m auto_daily report' generates a daily report.

    The report command should:
    1. Read today's log file from the log directory
    2. Generate a daily report using Ollama
    3. Save the report to the reports directory
    """
    import json
    from datetime import date
    from unittest.mock import AsyncMock, patch

    # Arrange: Create a temporary log directory with a log file
    log_dir = tmp_path / "logs"
    log_dir.mkdir()
    reports_dir = tmp_path / "reports"
    today = date.today()
    log_file = log_dir / f"{today.isoformat()}.jsonl"
    log_entry = {
        "timestamp": "2024-12-25T10:00:00",
        "window_info": {"app_name": "Code", "window_title": "test.py"},
        "ocr_text": "test content",
    }
    log_file.write_text(json.dumps(log_entry) + "\n")

    # Mock environment and Ollama
    monkeypatch.setenv("AUTO_DAILY_LOG_DIR", str(log_dir))

    mock_client = AsyncMock()
    mock_client.generate.return_value = "# 日報\n\n今日の作業内容..."

    with (
        patch("auto_daily.ollama.OllamaClient", return_value=mock_client),
        patch("auto_daily.get_reports_dir", return_value=reports_dir),
        patch("sys.argv", ["auto-daily", "report"]),
    ):
        from auto_daily import main

        # Act: Call main with report command
        main()

    # Assert: Ollama should have been called
    mock_client.generate.assert_called_once()


def test_report_with_date_option(tmp_path, monkeypatch) -> None:
    """Test that --date option allows generating report for a specific date.

    The --date option should:
    1. Accept a date in YYYY-MM-DD format
    2. Read the log file for that specific date
    3. Generate a report for that date
    """
    import json
    from unittest.mock import AsyncMock, patch

    # Arrange: Create a log file for a specific date
    log_dir = tmp_path / "logs"
    log_dir.mkdir()
    reports_dir = tmp_path / "reports"
    target_date = "2024-12-24"
    log_file = log_dir / f"{target_date}.jsonl"
    log_entry = {
        "timestamp": "2024-12-24T15:00:00",
        "window_info": {"app_name": "Safari", "window_title": "Google"},
        "ocr_text": "search results",
    }
    log_file.write_text(json.dumps(log_entry) + "\n")

    monkeypatch.setenv("AUTO_DAILY_LOG_DIR", str(log_dir))

    mock_client = AsyncMock()
    mock_client.generate.return_value = "# 日報 2024-12-24\n\n..."

    with (
        patch("auto_daily.ollama.OllamaClient", return_value=mock_client),
        patch("auto_daily.get_reports_dir", return_value=reports_dir),
        patch("sys.argv", ["auto-daily", "report", "--date", target_date]),
    ):
        from auto_daily import main

        # Act: Call main with report command and --date option
        main()

    # Assert: Ollama should have been called
    mock_client.generate.assert_called_once()


def test_report_saves_to_reports_dir(tmp_path, monkeypatch) -> None:
    """Test that generated reports are saved to ~/.auto-daily/reports/.

    The report command should:
    1. Save the generated report to the reports directory
    2. Use the filename format: daily_report_YYYY-MM-DD.md
    """
    import json
    from datetime import date
    from unittest.mock import AsyncMock, patch

    # Arrange: Setup directories
    log_dir = tmp_path / "logs"
    log_dir.mkdir()
    reports_dir = tmp_path / "reports"

    today = date.today()
    log_file = log_dir / f"{today.isoformat()}.jsonl"
    log_entry = {
        "timestamp": "2024-12-25T10:00:00",
        "window_info": {"app_name": "Code", "window_title": "test.py"},
        "ocr_text": "test content",
    }
    log_file.write_text(json.dumps(log_entry) + "\n")

    monkeypatch.setenv("AUTO_DAILY_LOG_DIR", str(log_dir))

    mock_client = AsyncMock()
    mock_client.generate.return_value = "# 日報\n\n今日の作業内容..."

    with (
        patch("auto_daily.ollama.OllamaClient", return_value=mock_client),
        patch("auto_daily.get_reports_dir", return_value=reports_dir),
        patch("sys.argv", ["auto-daily", "report"]),
    ):
        from auto_daily import main

        # Act: Call main with report command
        main()

    # Assert: Report file should exist in reports directory
    expected_file = reports_dir / f"daily_report_{today.isoformat()}.md"
    assert expected_file.exists()
    assert "日報" in expected_file.read_text()


def test_report_outputs_path(tmp_path, monkeypatch, capsys) -> None:
    """Test that the report command outputs the saved file path.

    The report command should:
    1. Print the path of the saved report file to stdout
    2. Allow users to easily locate the generated report
    """
    import json
    from datetime import date
    from unittest.mock import AsyncMock, patch

    # Arrange: Setup directories
    log_dir = tmp_path / "logs"
    log_dir.mkdir()
    reports_dir = tmp_path / "reports"

    today = date.today()
    log_file = log_dir / f"{today.isoformat()}.jsonl"
    log_entry = {
        "timestamp": "2024-12-25T10:00:00",
        "window_info": {"app_name": "Code", "window_title": "test.py"},
        "ocr_text": "test content",
    }
    log_file.write_text(json.dumps(log_entry) + "\n")

    monkeypatch.setenv("AUTO_DAILY_LOG_DIR", str(log_dir))

    mock_client = AsyncMock()
    mock_client.generate.return_value = "# 日報\n\n今日の作業内容..."

    with (
        patch("auto_daily.ollama.OllamaClient", return_value=mock_client),
        patch("auto_daily.get_reports_dir", return_value=reports_dir),
        patch("sys.argv", ["auto-daily", "report"]),
    ):
        from auto_daily import main

        # Act: Call main with report command
        main()

    # Assert: The output should contain the file path
    captured = capsys.readouterr()
    expected_file = reports_dir / f"daily_report_{today.isoformat()}.md"
    assert str(expected_file) in captured.stdout
