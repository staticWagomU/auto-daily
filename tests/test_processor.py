"""Tests for window change processor with Slack context integration."""

import json
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

from auto_daily.processor import process_window_change


class TestSlackContextAdded:
    """Test that Slack context is added when processing Slack windows."""

    def test_slack_context_added(self, tmp_path: Path) -> None:
        """Verify slack_context is extracted and passed to append_log_hourly for Slack windows.

        When the window app is "Slack", the processor should:
        1. Call parse_slack_title() with the window title
        2. Pass the extracted slack_context to append_log_hourly()
        """
        old_window = {"app_name": "Terminal", "window_title": "zsh"}
        new_window = {"app_name": "Slack", "window_title": "#dev-team | Company"}

        with patch("auto_daily.processor.capture_screen") as mock_capture:
            mock_capture.return_value = str(tmp_path / "test.png")
            with patch("auto_daily.processor.perform_ocr") as mock_ocr:
                mock_ocr.return_value = "test text"
                with patch("auto_daily.processor.append_log_hourly") as mock_log:
                    mock_log.return_value = tmp_path / "log.jsonl"
                    with patch("auto_daily.processor.cleanup_image"):
                        process_window_change(old_window, new_window, tmp_path)

                    # Verify append_log_hourly was called with slack_context
                    mock_log.assert_called_once()
                    call_kwargs = mock_log.call_args
                    # Check that slack_context is passed (either as kwarg or 4th positional arg)
                    if call_kwargs.kwargs:
                        assert "slack_context" in call_kwargs.kwargs
                        slack_context = call_kwargs.kwargs["slack_context"]
                    else:
                        # If passed as positional arg, it should be the 4th argument
                        assert len(call_kwargs.args) >= 4
                        slack_context = call_kwargs.args[3]

                    assert slack_context is not None
                    assert slack_context["channel"] == "dev-team"
                    assert slack_context["workspace"] == "Company"
                    assert slack_context["dm_user"] is None
                    assert slack_context["is_thread"] is False


class TestNonSlackNoContext:
    """Test that non-Slack apps don't get Slack context."""

    def test_non_slack_no_context(self, tmp_path: Path) -> None:
        """Verify slack_context is None for non-Slack applications.

        When the window app is not "Slack", the processor should:
        1. Not call parse_slack_title()
        2. Pass slack_context=None to append_log_hourly()
        """
        old_window = {"app_name": "Slack", "window_title": "#dev-team | Company"}
        new_window = {"app_name": "Safari", "window_title": "Google Search"}

        with patch("auto_daily.processor.capture_screen") as mock_capture:
            mock_capture.return_value = str(tmp_path / "test.png")
            with patch("auto_daily.processor.perform_ocr") as mock_ocr:
                mock_ocr.return_value = "web page content"
                with patch("auto_daily.processor.append_log_hourly") as mock_log:
                    mock_log.return_value = tmp_path / "log.jsonl"
                    with patch("auto_daily.processor.cleanup_image"):
                        process_window_change(old_window, new_window, tmp_path)

                    # Verify append_log_hourly was called with slack_context=None
                    mock_log.assert_called_once()
                    call_kwargs = mock_log.call_args
                    assert "slack_context" in call_kwargs.kwargs
                    assert call_kwargs.kwargs["slack_context"] is None


class TestLogInDateDirectory:
    """Test that processor uses append_log_hourly for date-based directory logging."""

    def test_log_in_date_directory(self, tmp_path: Path) -> None:
        """Verify processor uses append_log_hourly to save logs in date directories.

        When process_window_change is called:
        1. It should use append_log_hourly instead of append_log
        2. Logs should be saved in logs/YYYY-MM-DD/activity_HH.jsonl format
        3. slack_context should be passed to append_log_hourly
        """
        old_window = {"app_name": "Terminal", "window_title": "zsh"}
        new_window = {"app_name": "Slack", "window_title": "#dev-team | Company"}

        log_base = tmp_path / "logs"
        log_base.mkdir()

        with patch("auto_daily.processor.capture_screen") as mock_capture:
            mock_capture.return_value = str(tmp_path / "test.png")
            with patch("auto_daily.processor.perform_ocr") as mock_ocr:
                mock_ocr.return_value = "test text"
                with patch("auto_daily.processor.cleanup_image"):
                    # Mock datetime to control the directory/file names
                    with patch("auto_daily.logger.datetime") as mock_dt:
                        mock_dt.now.return_value = datetime(2025, 12, 26, 14, 30, 0)
                        mock_dt.side_effect = lambda *args, **kwargs: datetime(
                            *args, **kwargs
                        )

                        result = process_window_change(old_window, new_window, log_base)

        assert result is True

        # Verify log was saved in date directory with hourly format
        expected_date_dir = log_base / "2025-12-26"
        expected_log_file = expected_date_dir / "activity_14.jsonl"

        assert expected_date_dir.exists(), (
            f"Date directory {expected_date_dir} should exist"
        )
        assert expected_log_file.exists(), f"Log file {expected_log_file} should exist"

        # Verify log content includes slack_context
        with open(expected_log_file) as f:
            entry = json.loads(f.readline())

        assert entry["window_info"] == new_window
        assert entry["ocr_text"] == "test text"
        assert entry["slack_context"]["channel"] == "dev-team"
        assert entry["slack_context"]["workspace"] == "Company"
