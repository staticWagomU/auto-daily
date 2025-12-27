"""Tests for periodic capture scheduler."""

import time
from pathlib import Path
from unittest.mock import MagicMock, patch

from auto_daily.scheduler import HourlySummaryScheduler, PeriodicCapture


class TestPeriodicCapture:
    """Test periodic capture functionality."""

    def test_periodic_capture(self, tmp_path: Path) -> None:
        """Verify capture is executed at regular intervals."""
        mock_callback = MagicMock()

        # Use a short interval for testing
        scheduler = PeriodicCapture(
            callback=mock_callback,
            log_dir=tmp_path,
            interval=0.05,  # 50ms for testing
        )

        # Mock is_system_active to always return True in tests
        with patch("auto_daily.scheduler.is_system_active", return_value=True):
            scheduler.start()
            time.sleep(0.5)  # Wait for ~10 intervals (more generous)
            scheduler.stop()

        # Should have been called at least 3 times
        assert mock_callback.call_count >= 3

    def test_coexistence_with_window_trigger(self, tmp_path: Path) -> None:
        """Verify periodic capture can run alongside window change callbacks."""
        periodic_callback = MagicMock()
        window_callback = MagicMock()

        scheduler = PeriodicCapture(
            callback=periodic_callback,
            log_dir=tmp_path,
            interval=0.05,  # 50ms for testing
        )

        # Mock is_system_active to always return True in tests
        with patch("auto_daily.scheduler.is_system_active", return_value=True):
            scheduler.start()

            # Simulate window change callback being called independently
            window_callback("old", "new")
            window_callback("old2", "new2")

            time.sleep(0.4)  # More generous wait time
            scheduler.stop()

        # Both should have been called
        assert periodic_callback.call_count >= 2
        assert window_callback.call_count == 2

    def test_stop_periodic_capture(self, tmp_path: Path) -> None:
        """Verify periodic capture stops when stop() is called."""
        mock_callback = MagicMock()

        scheduler = PeriodicCapture(
            callback=mock_callback,
            log_dir=tmp_path,
            interval=0.05,  # 50ms for testing
        )

        # Mock is_system_active to always return True in tests
        with patch("auto_daily.scheduler.is_system_active", return_value=True):
            scheduler.start()
            time.sleep(0.2)
            scheduler.stop()

            call_count_after_stop = mock_callback.call_count
            time.sleep(0.2)

        # Should not have been called after stop
        assert mock_callback.call_count == call_count_after_stop

    def test_callback_receives_log_dir(self, tmp_path: Path) -> None:
        """Verify callback receives the log directory."""
        mock_callback = MagicMock()

        scheduler = PeriodicCapture(
            callback=mock_callback,
            log_dir=tmp_path,
            interval=0.05,  # 50ms for testing
        )

        # Mock is_system_active to always return True in tests
        with patch("auto_daily.scheduler.is_system_active", return_value=True):
            scheduler.start()
            time.sleep(0.3)  # More generous wait time
            scheduler.stop()

        # Check that callback was called with the log_dir
        mock_callback.assert_called_with(tmp_path)


class TestPeriodicCaptureWithProcessor:
    """Test periodic capture with actual processor integration."""

    def test_periodic_capture_calls_processor(self, tmp_path: Path) -> None:
        """Verify periodic capture calls the processor function."""
        with (
            patch("auto_daily.scheduler.process_periodic_capture") as mock_process,
            patch("auto_daily.scheduler.is_system_active", return_value=True),
        ):
            scheduler = PeriodicCapture(
                callback=mock_process,
                log_dir=tmp_path,
                interval=0.05,  # 50ms for testing
            )

            scheduler.start()
            time.sleep(0.3)  # More generous wait time
            scheduler.stop()

            assert mock_process.call_count >= 1


class TestHourlySummaryScheduler:
    """Test hourly summary scheduler functionality."""

    def test_hourly_summary_scheduler(self, tmp_path: Path) -> None:
        """Test that HourlySummaryScheduler calls callback at scheduled times.

        The scheduler should:
        1. Accept a callback function and log/summaries directories
        2. Call the callback when triggered
        3. Stop cleanly when stop() is called
        """
        mock_callback = MagicMock()
        log_dir = tmp_path / "logs"
        log_dir.mkdir()
        summaries_dir = tmp_path / "summaries"
        summaries_dir.mkdir()

        scheduler = HourlySummaryScheduler(
            callback=mock_callback,
            log_dir=log_dir,
            summaries_dir=summaries_dir,
            # For testing, use a very short check interval
            check_interval=0.1,
        )

        scheduler.start()
        # Trigger manually for testing
        scheduler.trigger_summary()
        time.sleep(0.15)
        scheduler.stop()

        # Callback should have been called at least once
        assert mock_callback.call_count >= 1

    def test_hourly_summary_scheduler_passes_dirs(self, tmp_path: Path) -> None:
        """Test that callback receives log_dir and summaries_dir."""
        mock_callback = MagicMock()
        log_dir = tmp_path / "logs"
        log_dir.mkdir()
        summaries_dir = tmp_path / "summaries"
        summaries_dir.mkdir()

        scheduler = HourlySummaryScheduler(
            callback=mock_callback,
            log_dir=log_dir,
            summaries_dir=summaries_dir,
            check_interval=0.1,
        )

        scheduler.start()
        scheduler.trigger_summary()
        time.sleep(0.15)
        scheduler.stop()

        # Check callback was called with correct arguments
        mock_callback.assert_called_with(log_dir, summaries_dir)
