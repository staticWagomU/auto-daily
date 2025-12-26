"""Integration tests for window change processing pipeline."""

from pathlib import Path
from unittest.mock import patch

from auto_daily.processor import process_window_change


class TestCaptureOnWindowChange:
    """Test that screen capture is triggered on window change."""

    def test_capture_on_window_change(self, tmp_path: Path) -> None:
        """Verify capture_screen is called when processing window change."""
        old_window = {"app_name": "Terminal", "window_title": "zsh"}
        new_window = {"app_name": "Safari", "window_title": "Google"}

        with patch("auto_daily.capture_pipeline.capture_screen") as mock_capture:
            mock_capture.return_value = str(tmp_path / "test.png")
            with patch("auto_daily.capture_pipeline.perform_ocr") as mock_ocr:
                mock_ocr.return_value = "test text"
                with patch("auto_daily.capture_pipeline.append_log_hourly") as mock_log:
                    mock_log.return_value = tmp_path / "log.jsonl"
                    with patch("auto_daily.capture_pipeline.cleanup_image"):
                        process_window_change(old_window, new_window, tmp_path)

            mock_capture.assert_called_once()


class TestOcrOnCapture:
    """Test that OCR is performed on captured image."""

    def test_ocr_on_capture(self, tmp_path: Path) -> None:
        """Verify perform_ocr is called with the captured image path."""
        old_window = {"app_name": "Terminal", "window_title": "zsh"}
        new_window = {"app_name": "Safari", "window_title": "Google"}
        captured_image = str(tmp_path / "captured.png")

        with patch("auto_daily.capture_pipeline.capture_screen") as mock_capture:
            mock_capture.return_value = captured_image
            with patch("auto_daily.capture_pipeline.perform_ocr") as mock_ocr:
                mock_ocr.return_value = "extracted text"
                with patch("auto_daily.capture_pipeline.append_log_hourly") as mock_log:
                    mock_log.return_value = tmp_path / "log.jsonl"
                    with patch("auto_daily.capture_pipeline.cleanup_image"):
                        process_window_change(old_window, new_window, tmp_path)

            mock_ocr.assert_called_once_with(captured_image)


class TestLogOnWindowChange:
    """Test that window info and OCR result are logged."""

    def test_log_on_window_change(self, tmp_path: Path) -> None:
        """Verify append_log_hourly is called with window info and OCR text."""
        old_window = {"app_name": "Terminal", "window_title": "zsh"}
        new_window = {"app_name": "Safari", "window_title": "Google"}
        ocr_text = "Page content here"

        with patch("auto_daily.capture_pipeline.capture_screen") as mock_capture:
            mock_capture.return_value = str(tmp_path / "test.png")
            with patch("auto_daily.capture_pipeline.perform_ocr") as mock_ocr:
                mock_ocr.return_value = ocr_text
                with patch("auto_daily.capture_pipeline.append_log_hourly") as mock_log:
                    mock_log.return_value = tmp_path / "log.jsonl"
                    with patch("auto_daily.capture_pipeline.cleanup_image"):
                        process_window_change(old_window, new_window, tmp_path)

            mock_log.assert_called_once_with(
                tmp_path, new_window, ocr_text, slack_context=None
            )


class TestCleanupAfterProcessing:
    """Test that captured image is cleaned up after processing."""

    def test_cleanup_after_processing(self, tmp_path: Path) -> None:
        """Verify cleanup_image is called with the captured image path."""
        old_window = {"app_name": "Terminal", "window_title": "zsh"}
        new_window = {"app_name": "Safari", "window_title": "Google"}
        captured_image = str(tmp_path / "captured.png")

        with patch("auto_daily.capture_pipeline.capture_screen") as mock_capture:
            mock_capture.return_value = captured_image
            with patch("auto_daily.capture_pipeline.perform_ocr") as mock_ocr:
                mock_ocr.return_value = "text"
                with patch("auto_daily.capture_pipeline.append_log_hourly") as mock_log:
                    mock_log.return_value = tmp_path / "log.jsonl"
                    with patch(
                        "auto_daily.capture_pipeline.cleanup_image"
                    ) as mock_cleanup:
                        process_window_change(old_window, new_window, tmp_path)

                        mock_cleanup.assert_called_once_with(captured_image)


class TestProcessWindowChangeEdgeCases:
    """Test edge cases in window change processing."""

    def test_skip_processing_when_capture_fails(self, tmp_path: Path) -> None:
        """Verify processing stops gracefully when capture fails."""
        old_window = {"app_name": "Terminal", "window_title": "zsh"}
        new_window = {"app_name": "Safari", "window_title": "Google"}

        with patch("auto_daily.capture_pipeline.capture_screen") as mock_capture:
            mock_capture.return_value = None  # Capture failed
            with patch("auto_daily.capture_pipeline.perform_ocr") as mock_ocr:
                with patch("auto_daily.capture_pipeline.append_log_hourly") as mock_log:
                    with patch(
                        "auto_daily.capture_pipeline.cleanup_image"
                    ) as mock_cleanup:
                        result = process_window_change(old_window, new_window, tmp_path)

                        assert result is False
                        mock_ocr.assert_not_called()
                        mock_log.assert_not_called()
                        mock_cleanup.assert_not_called()
