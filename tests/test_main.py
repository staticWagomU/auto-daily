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
    from datetime import date, datetime
    from unittest.mock import AsyncMock, patch

    import auto_daily
    from auto_daily.logger import get_log_filename

    # Arrange: Create a temporary log directory with a log file
    log_dir = tmp_path / "logs"
    log_dir.mkdir()
    reports_dir = tmp_path / "reports"
    today = date.today()
    # Use correct log filename format (activity_YYYY-MM-DD.jsonl)
    log_file = log_dir / get_log_filename(datetime.combine(today, datetime.min.time()))
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
        patch.object(auto_daily, "OllamaClient", return_value=mock_client),
        patch.object(auto_daily, "get_reports_dir", return_value=reports_dir),
        patch("sys.argv", ["auto-daily", "report"]),
    ):
        # Act: Call main with report command
        auto_daily.main()

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
    from datetime import datetime
    from unittest.mock import AsyncMock, patch

    import auto_daily
    from auto_daily.logger import get_log_filename

    # Arrange: Create a log file for a specific date
    log_dir = tmp_path / "logs"
    log_dir.mkdir()
    reports_dir = tmp_path / "reports"
    target_date = "2024-12-24"
    # Use correct log filename format (activity_YYYY-MM-DD.jsonl)
    target_datetime = datetime.fromisoformat(f"{target_date}T00:00:00")
    log_file = log_dir / get_log_filename(target_datetime)
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
        patch.object(auto_daily, "OllamaClient", return_value=mock_client),
        patch.object(auto_daily, "get_reports_dir", return_value=reports_dir),
        patch("sys.argv", ["auto-daily", "report", "--date", target_date]),
    ):
        # Act: Call main with report command and --date option
        auto_daily.main()

    # Assert: Ollama should have been called
    mock_client.generate.assert_called_once()


def test_report_saves_to_reports_dir(tmp_path, monkeypatch) -> None:
    """Test that generated reports are saved to ~/.auto-daily/reports/.

    The report command should:
    1. Save the generated report to the reports directory
    2. Use the filename format: daily_report_YYYY-MM-DD.md
    """
    import json
    from datetime import date, datetime
    from unittest.mock import AsyncMock, patch

    import auto_daily
    from auto_daily.logger import get_log_filename

    # Arrange: Setup directories
    log_dir = tmp_path / "logs"
    log_dir.mkdir()
    reports_dir = tmp_path / "reports"

    today = date.today()
    # Use correct log filename format (activity_YYYY-MM-DD.jsonl)
    log_file = log_dir / get_log_filename(datetime.combine(today, datetime.min.time()))
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
        patch.object(auto_daily, "OllamaClient", return_value=mock_client),
        patch.object(auto_daily, "get_reports_dir", return_value=reports_dir),
        patch("sys.argv", ["auto-daily", "report"]),
    ):
        # Act: Call main with report command
        auto_daily.main()

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
    from datetime import date, datetime
    from unittest.mock import AsyncMock, patch

    import auto_daily
    from auto_daily.logger import get_log_filename

    # Arrange: Setup directories
    log_dir = tmp_path / "logs"
    log_dir.mkdir()
    reports_dir = tmp_path / "reports"

    today = date.today()
    # Use correct log filename format (activity_YYYY-MM-DD.jsonl)
    log_file = log_dir / get_log_filename(datetime.combine(today, datetime.min.time()))
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
        patch.object(auto_daily, "OllamaClient", return_value=mock_client),
        patch.object(auto_daily, "get_reports_dir", return_value=reports_dir),
        patch("sys.argv", ["auto-daily", "report"]),
    ):
        # Act: Call main with report command
        auto_daily.main()

    # Assert: The output should contain the file path
    captured = capsys.readouterr()
    expected_file = reports_dir / f"daily_report_{today.isoformat()}.md"
    assert str(expected_file) in captured.out


def test_report_uses_correct_log_filename(tmp_path, monkeypatch) -> None:
    """Test that report command uses the same log filename format as logger.py.

    The report command should:
    1. Use logger.get_log_filename() to construct the log file path
    2. Look for files in 'activity_YYYY-MM-DD.jsonl' format
    3. Match the format used by logger.append_log()

    This is a regression test for PBI-017: report command was looking for
    'YYYY-MM-DD.jsonl' instead of 'activity_YYYY-MM-DD.jsonl'.
    """
    import json
    from datetime import date, datetime
    from unittest.mock import AsyncMock, patch

    import auto_daily
    from auto_daily.logger import get_log_filename

    # Arrange: Create a log file with the CORRECT format (activity_YYYY-MM-DD.jsonl)
    log_dir = tmp_path / "logs"
    log_dir.mkdir()
    reports_dir = tmp_path / "reports"

    today = date.today()
    # Use get_log_filename to ensure we're using the same format as logger.py
    correct_filename = get_log_filename(datetime.combine(today, datetime.min.time()))
    log_file = log_dir / correct_filename

    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "window_info": {"app_name": "Code", "window_title": "test.py"},
        "ocr_text": "Test content for PBI-017",
    }
    log_file.write_text(json.dumps(log_entry) + "\n")

    # Also verify the correct format is activity_YYYY-MM-DD.jsonl
    assert correct_filename == f"activity_{today.isoformat()}.jsonl"

    monkeypatch.setenv("AUTO_DAILY_LOG_DIR", str(log_dir))

    mock_client = AsyncMock()
    mock_client.generate.return_value = "# 日報\n\nPBI-017 修正確認用"

    with (
        patch.object(auto_daily, "OllamaClient", return_value=mock_client),
        patch.object(auto_daily, "get_reports_dir", return_value=reports_dir),
        patch("sys.argv", ["auto-daily", "report"]),
    ):
        # Act: Call main with report command
        auto_daily.main()

    # Assert: Ollama should have been called (meaning log file was found)
    mock_client.generate.assert_called_once()


# ============================================================
# PBI-033: Permission check on startup
# ============================================================


def test_permission_warning_on_start(capsys) -> None:
    """Test that a warning is displayed when permissions are missing on start.

    The main function should:
    1. Check permissions when --start is passed
    2. Display a warning message if screen recording permission is missing
    3. Display a warning message if accessibility permission is missing
    4. Suggest running setup-permissions.sh
    5. Exit with code 1 when permissions are missing
    """
    from unittest.mock import patch

    # Arrange: Mock permissions to return all False
    mock_perms = {"screen_recording": False, "accessibility": False}

    with (
        patch("auto_daily.check_all_permissions", return_value=mock_perms),
        patch("sys.argv", ["auto-daily", "--start"]),
    ):
        from auto_daily import main

        # Act: Call main with --start (should exit with error)
        try:
            main()
            raise AssertionError("Expected SystemExit")
        except SystemExit as e:
            # Assert: Should exit with code 1
            assert e.code == 1

    # Assert: Should display warning messages
    captured = capsys.readouterr()
    assert (
        "Screen recording permission" in captured.out
        or "screen recording" in captured.out.lower()
    )
    assert (
        "Accessibility permission" in captured.out
        or "accessibility" in captured.out.lower()
    )
    assert "setup-permissions.sh" in captured.out


def test_start_with_permissions(capsys) -> None:
    """Test that monitoring starts normally when all permissions are granted.

    The main function should:
    1. Check permissions when --start is passed
    2. Continue to start monitoring if all permissions are granted
    3. Not display permission warning messages
    """
    from unittest.mock import MagicMock, patch

    # Arrange: Mock permissions to return all True
    mock_perms = {"screen_recording": True, "accessibility": True}
    mock_monitor_instance = MagicMock()
    mock_monitor_class = MagicMock(return_value=mock_monitor_instance)

    with (
        patch("auto_daily.check_all_permissions", return_value=mock_perms),
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

    # Assert: No permission warning messages
    captured = capsys.readouterr()
    assert (
        "permission" not in captured.out.lower()
        or "Screen recording permission" not in captured.out
    )


# ============================================================
# PBI-016: Ollama connection check
# ============================================================


def test_start_without_ollama(capsys) -> None:
    """Test that app starts successfully even when Ollama is not available.

    The main function should:
    1. Check Ollama connection when --start is passed
    2. Display a warning message if Ollama is not available
    3. Continue to start window monitoring regardless
    """
    from unittest.mock import MagicMock, patch

    # Arrange: Mock permissions as granted, but Ollama as unavailable
    mock_perms = {"screen_recording": True, "accessibility": True}
    mock_monitor_instance = MagicMock()
    mock_monitor_class = MagicMock(return_value=mock_monitor_instance)

    with (
        patch("auto_daily.check_all_permissions", return_value=mock_perms),
        patch("auto_daily.check_ollama_connection", return_value=False),
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
    # (even though Ollama is not available)
    mock_monitor_class.assert_called_once()
    mock_monitor_instance.start.assert_called_once()


def test_start_warns_without_ollama(capsys) -> None:
    """Test that a warning is displayed when Ollama is not available on start.

    The main function should:
    1. Check Ollama connection when --start is passed
    2. Display a warning message if Ollama is not available
    3. Include the Ollama URL in the warning message
    4. Indicate that report generation will not work
    """
    from unittest.mock import MagicMock, patch

    # Arrange: Mock permissions as granted, but Ollama as unavailable
    mock_perms = {"screen_recording": True, "accessibility": True}
    mock_monitor_instance = MagicMock()
    mock_monitor_class = MagicMock(return_value=mock_monitor_instance)

    with (
        patch("auto_daily.check_all_permissions", return_value=mock_perms),
        patch("auto_daily.check_ollama_connection", return_value=False),
        patch("auto_daily.get_ollama_base_url", return_value="http://localhost:11434"),
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

    # Assert: Warning should be displayed
    captured = capsys.readouterr()
    assert "Warning" in captured.out or "warning" in captured.out.lower()
    assert "Ollama" in captured.out
    assert "http://localhost:11434" in captured.out
    assert "Report" in captured.out or "report" in captured.out.lower()


def test_report_fails_without_ollama(tmp_path, monkeypatch, capsys) -> None:
    """Test that report command fails when Ollama is not available.

    The report command should:
    1. Check Ollama connection before generating report
    2. Exit with code 1 if Ollama is not available
    3. Display an error message with the Ollama URL
    """
    import json
    from datetime import date, datetime
    from unittest.mock import patch

    from auto_daily.logger import get_log_filename

    # Arrange: Create a log file (report should fail before reading it)
    log_dir = tmp_path / "logs"
    log_dir.mkdir()

    today = date.today()
    log_file = log_dir / get_log_filename(datetime.combine(today, datetime.min.time()))
    log_entry = {
        "timestamp": "2024-12-25T10:00:00",
        "window_info": {"app_name": "Code", "window_title": "test.py"},
        "ocr_text": "test content",
    }
    log_file.write_text(json.dumps(log_entry) + "\n")

    monkeypatch.setenv("AUTO_DAILY_LOG_DIR", str(log_dir))

    with (
        patch("auto_daily.check_ollama_connection", return_value=False),
        patch("auto_daily.get_ollama_base_url", return_value="http://localhost:11434"),
        patch("sys.argv", ["auto-daily", "report"]),
    ):
        from auto_daily import main

        # Act: Call main with report command (should exit with error)
        try:
            main()
            raise AssertionError("Expected SystemExit")
        except SystemExit as e:
            # Assert: Should exit with code 1
            assert e.code == 1

    # Assert: Error message should be displayed
    captured = capsys.readouterr()
    assert "Error" in captured.out or "error" in captured.out.lower()
    assert "Ollama" in captured.out
    assert "http://localhost:11434" in captured.out


def test_report_fails_with_invalid_ollama_url(tmp_path, monkeypatch, capsys) -> None:
    """Test that report command fails when OLLAMA_BASE_URL is invalid.

    The report command should:
    1. Check connection to the configured OLLAMA_BASE_URL
    2. Exit with code 1 if the URL is unreachable
    3. Display the configured URL in the error message
    """
    import json
    from datetime import date, datetime
    from unittest.mock import patch

    from auto_daily.logger import get_log_filename

    # Arrange: Create a log file
    log_dir = tmp_path / "logs"
    log_dir.mkdir()

    today = date.today()
    log_file = log_dir / get_log_filename(datetime.combine(today, datetime.min.time()))
    log_entry = {
        "timestamp": "2024-12-25T10:00:00",
        "window_info": {"app_name": "Code", "window_title": "test.py"},
        "ocr_text": "test content",
    }
    log_file.write_text(json.dumps(log_entry) + "\n")

    monkeypatch.setenv("AUTO_DAILY_LOG_DIR", str(log_dir))

    # Use a custom invalid URL
    custom_url = "http://invalid-host:9999"

    with (
        patch("auto_daily.check_ollama_connection", return_value=False),
        patch("auto_daily.get_ollama_base_url", return_value=custom_url),
        patch("sys.argv", ["auto-daily", "report"]),
    ):
        from auto_daily import main

        # Act: Call main with report command (should exit with error)
        try:
            main()
            raise AssertionError("Expected SystemExit")
        except SystemExit as e:
            # Assert: Should exit with code 1
            assert e.code == 1

    # Assert: Error message should include the custom URL
    captured = capsys.readouterr()
    assert custom_url in captured.out


def test_report_with_existing_log(tmp_path, monkeypatch, capsys) -> None:
    """Test that report succeeds when activity_YYYY-MM-DD.jsonl exists.

    This test verifies the end-to-end flow:
    1. Log file exists in the correct format
    2. Report generation is successful
    3. Report is saved to the correct location

    This is a regression test for PBI-017.
    """
    import json
    from datetime import datetime
    from unittest.mock import AsyncMock, patch

    import auto_daily
    from auto_daily.logger import get_log_filename

    # Arrange: Create a log file with activity_YYYY-MM-DD.jsonl format
    log_dir = tmp_path / "logs"
    log_dir.mkdir()
    reports_dir = tmp_path / "reports"

    target_date = "2024-12-24"
    target_datetime = datetime.fromisoformat(f"{target_date}T00:00:00")
    correct_filename = get_log_filename(target_datetime)
    log_file = log_dir / correct_filename

    log_entry = {
        "timestamp": f"{target_date}T15:00:00",
        "window_info": {"app_name": "Safari", "window_title": "Research"},
        "ocr_text": "Found important information",
    }
    log_file.write_text(json.dumps(log_entry) + "\n")

    monkeypatch.setenv("AUTO_DAILY_LOG_DIR", str(log_dir))

    mock_client = AsyncMock()
    mock_client.generate.return_value = "# 日報 2024-12-24\n\n調査作業を実施"

    with (
        patch.object(auto_daily, "OllamaClient", return_value=mock_client),
        patch.object(auto_daily, "get_reports_dir", return_value=reports_dir),
        patch("sys.argv", ["auto-daily", "report", "--date", target_date]),
    ):
        # Act: Call main with report command
        auto_daily.main()

    # Assert: Report should be generated and saved
    mock_client.generate.assert_called_once()
    expected_report = reports_dir / f"daily_report_{target_date}.md"
    assert expected_report.exists()
    assert "日報" in expected_report.read_text()


# ============================================================
# PBI-032: Calendar integration in report command
# ============================================================


def test_report_with_calendar_option(tmp_path, monkeypatch) -> None:
    """Test that --with-calendar option enables calendar integration.

    The --with-calendar option should:
    1. Be accepted by the report command
    2. Fetch calendar events for the target date
    3. Match events with logs
    4. Include calendar information in the generated prompt
    """
    import json
    from datetime import UTC, date, datetime
    from unittest.mock import AsyncMock, patch

    import auto_daily
    from auto_daily.calendar import CalendarEvent
    from auto_daily.logger import get_log_filename

    # Arrange: Create a log file
    log_dir = tmp_path / "logs"
    log_dir.mkdir()
    reports_dir = tmp_path / "reports"

    today = date.today()
    log_file = log_dir / get_log_filename(datetime.combine(today, datetime.min.time()))
    log_entry = {
        "timestamp": datetime.combine(today, datetime.min.time())
        .replace(hour=9, minute=15)
        .isoformat(),
        "window_info": {"app_name": "Zoom", "window_title": "Team Meeting"},
        "ocr_text": "Meeting notes",
    }
    log_file.write_text(json.dumps(log_entry) + "\n")

    monkeypatch.setenv("AUTO_DAILY_LOG_DIR", str(log_dir))

    # Mock calendar events
    mock_events = [
        CalendarEvent(
            summary="Team Meeting",
            start=datetime.combine(today, datetime.min.time(), tzinfo=UTC).replace(
                hour=9
            ),
            end=datetime.combine(today, datetime.min.time(), tzinfo=UTC).replace(
                hour=10
            ),
            calendar_name="Work",
        )
    ]

    mock_client = AsyncMock()
    mock_client.generate.return_value = "# 日報\n\n予定通りにミーティングを実施"

    with (
        patch.object(auto_daily, "OllamaClient", return_value=mock_client),
        patch.object(auto_daily, "get_reports_dir", return_value=reports_dir),
        patch("auto_daily.get_all_events", return_value=mock_events),
        patch("sys.argv", ["auto-daily", "report", "--with-calendar"]),
    ):
        # Act: Call main with report command and --with-calendar
        auto_daily.main()

    # Assert: Ollama should have been called
    mock_client.generate.assert_called_once()

    # The prompt should contain calendar-related content
    call_args = mock_client.generate.call_args
    prompt = call_args.kwargs.get(
        "prompt", call_args.args[1] if len(call_args.args) > 1 else ""
    )
    # Prompt should mention the meeting or calendar info
    assert "Team Meeting" in prompt or "予定" in prompt
