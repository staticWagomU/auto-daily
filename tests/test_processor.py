"""Tests for window change processor with Slack context integration."""

from pathlib import Path
from unittest.mock import patch

from auto_daily.processor import process_window_change


class TestSlackContextAdded:
    """Test that Slack context is added when processing Slack windows."""

    def test_slack_context_added(self, tmp_path: Path) -> None:
        """Verify slack_context is extracted and passed to append_log for Slack windows.

        When the window app is "Slack", the processor should:
        1. Call parse_slack_title() with the window title
        2. Pass the extracted slack_context to append_log()
        """
        old_window = {"app_name": "Terminal", "window_title": "zsh"}
        new_window = {"app_name": "Slack", "window_title": "#dev-team | Company"}

        with patch("auto_daily.processor.capture_screen") as mock_capture:
            mock_capture.return_value = str(tmp_path / "test.png")
            with patch("auto_daily.processor.perform_ocr") as mock_ocr:
                mock_ocr.return_value = "test text"
                with patch("auto_daily.processor.append_log") as mock_log:
                    mock_log.return_value = str(tmp_path / "log.jsonl")
                    with patch("auto_daily.processor.cleanup_image"):
                        process_window_change(old_window, new_window, tmp_path)

                    # Verify append_log was called with slack_context
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
        2. Pass slack_context=None to append_log()
        """
        old_window = {"app_name": "Slack", "window_title": "#dev-team | Company"}
        new_window = {"app_name": "Safari", "window_title": "Google Search"}

        with patch("auto_daily.processor.capture_screen") as mock_capture:
            mock_capture.return_value = str(tmp_path / "test.png")
            with patch("auto_daily.processor.perform_ocr") as mock_ocr:
                mock_ocr.return_value = "web page content"
                with patch("auto_daily.processor.append_log") as mock_log:
                    mock_log.return_value = str(tmp_path / "log.jsonl")
                    with patch("auto_daily.processor.cleanup_image"):
                        process_window_change(old_window, new_window, tmp_path)

                    # Verify append_log was called with slack_context=None
                    mock_log.assert_called_once()
                    call_kwargs = mock_log.call_args
                    assert "slack_context" in call_kwargs.kwargs
                    assert call_kwargs.kwargs["slack_context"] is None
