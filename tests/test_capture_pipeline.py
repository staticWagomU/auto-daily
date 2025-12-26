"""Tests for capture pipeline module."""

from pathlib import Path
from unittest.mock import patch


class TestCaptureContext:
    """Test CaptureContext dataclass."""

    def test_capture_context_required_fields(self) -> None:
        """Verify CaptureContext requires window_info and log_dir."""
        from auto_daily.capture_pipeline import CaptureContext

        window_info = {"app_name": "Test App", "window_title": "Test Window"}
        log_dir = Path("/tmp/logs")

        context = CaptureContext(window_info=window_info, log_dir=log_dir)

        assert context.window_info == window_info
        assert context.log_dir == log_dir
        assert context.extract_slack_context is False  # Default value

    def test_capture_context_with_slack_extraction(self) -> None:
        """Verify CaptureContext can enable Slack context extraction."""
        from auto_daily.capture_pipeline import CaptureContext

        context = CaptureContext(
            window_info={"app_name": "Slack", "window_title": "#general | Company"},
            log_dir=Path("/tmp/logs"),
            extract_slack_context=True,
        )

        assert context.extract_slack_context is True


class TestExecuteCapturePipeline:
    """Test execute_capture_pipeline function."""

    def test_pipeline_success(self, tmp_path: Path) -> None:
        """Verify successful pipeline execution.

        The pipeline should:
        1. Capture the screen
        2. Perform OCR
        3. Log the activity
        4. Clean up the image
        5. Return True on success
        """
        from auto_daily.capture_pipeline import CaptureContext, execute_capture_pipeline

        context = CaptureContext(
            window_info={"app_name": "Test App", "window_title": "Test Window"},
            log_dir=tmp_path,
        )

        with patch("auto_daily.capture_pipeline.capture_screen") as mock_capture:
            mock_capture.return_value = str(tmp_path / "test.png")
            with patch("auto_daily.capture_pipeline.perform_ocr") as mock_ocr:
                mock_ocr.return_value = "test text"
                with patch("auto_daily.capture_pipeline.append_log_hourly") as mock_log:
                    mock_log.return_value = tmp_path / "log.jsonl"
                    with patch(
                        "auto_daily.capture_pipeline.cleanup_image"
                    ) as mock_cleanup:
                        result = execute_capture_pipeline(context)

        assert result is True
        mock_capture.assert_called_once_with(tmp_path)
        mock_ocr.assert_called_once()
        mock_log.assert_called_once()
        mock_cleanup.assert_called_once()

    def test_pipeline_returns_false_on_capture_failure(self, tmp_path: Path) -> None:
        """Verify pipeline returns False when capture fails."""
        from auto_daily.capture_pipeline import CaptureContext, execute_capture_pipeline

        context = CaptureContext(
            window_info={"app_name": "Test App", "window_title": "Test Window"},
            log_dir=tmp_path,
        )

        with patch("auto_daily.capture_pipeline.capture_screen") as mock_capture:
            mock_capture.return_value = None
            result = execute_capture_pipeline(context)

        assert result is False

    def test_pipeline_extracts_slack_context_when_enabled(self, tmp_path: Path) -> None:
        """Verify Slack context is extracted when extract_slack_context is True."""
        from auto_daily.capture_pipeline import CaptureContext, execute_capture_pipeline

        context = CaptureContext(
            window_info={"app_name": "Slack", "window_title": "#dev-team | Company"},
            log_dir=tmp_path,
            extract_slack_context=True,
        )

        with patch("auto_daily.capture_pipeline.capture_screen") as mock_capture:
            mock_capture.return_value = str(tmp_path / "test.png")
            with patch("auto_daily.capture_pipeline.perform_ocr") as mock_ocr:
                mock_ocr.return_value = "test text"
                with patch("auto_daily.capture_pipeline.append_log_hourly") as mock_log:
                    mock_log.return_value = tmp_path / "log.jsonl"
                    with patch("auto_daily.capture_pipeline.cleanup_image"):
                        execute_capture_pipeline(context)

                    # Verify slack_context was passed
                    call_kwargs = mock_log.call_args
                    assert "slack_context" in call_kwargs.kwargs
                    slack_context = call_kwargs.kwargs["slack_context"]
                    assert slack_context is not None
                    assert slack_context["channel"] == "dev-team"

    def test_pipeline_no_slack_context_when_disabled(self, tmp_path: Path) -> None:
        """Verify no Slack context extraction when extract_slack_context is False."""
        from auto_daily.capture_pipeline import CaptureContext, execute_capture_pipeline

        context = CaptureContext(
            window_info={"app_name": "Slack", "window_title": "#dev-team | Company"},
            log_dir=tmp_path,
            extract_slack_context=False,  # Disabled
        )

        with patch("auto_daily.capture_pipeline.capture_screen") as mock_capture:
            mock_capture.return_value = str(tmp_path / "test.png")
            with patch("auto_daily.capture_pipeline.perform_ocr") as mock_ocr:
                mock_ocr.return_value = "test text"
                with patch("auto_daily.capture_pipeline.append_log_hourly") as mock_log:
                    mock_log.return_value = tmp_path / "log.jsonl"
                    with patch("auto_daily.capture_pipeline.cleanup_image"):
                        execute_capture_pipeline(context)

                    # Verify slack_context was not passed or is None
                    call_kwargs = mock_log.call_args
                    slack_context = call_kwargs.kwargs.get("slack_context")
                    assert slack_context is None
