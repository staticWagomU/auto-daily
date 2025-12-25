"""Integration tests for system activity check integration."""

import time
from pathlib import Path
from unittest.mock import MagicMock, patch

from auto_daily.scheduler import PeriodicCapture
from auto_daily.window_monitor import WindowMonitor


def test_periodic_capture_checks_system_activity(tmp_path: Path):
    """Verify PeriodicCapture checks is_system_active before callback."""
    mock_callback = MagicMock()

    with patch("auto_daily.scheduler.is_system_active") as mock_active:
        mock_active.return_value = False

        scheduler = PeriodicCapture(
            callback=mock_callback,
            log_dir=tmp_path,
            interval=0.1,
        )

        scheduler.start()
        time.sleep(0.25)
        scheduler.stop()

        # Should have checked activity but never called callback
        assert mock_active.called
        assert mock_callback.call_count == 0

        # Now set to True
        mock_active.return_value = True
        mock_callback.reset_mock()

        scheduler = PeriodicCapture(
            callback=mock_callback,
            log_dir=tmp_path,
            interval=0.1,
        )

        scheduler.start()
        time.sleep(0.25)
        scheduler.stop()

        # Should have called callback
        assert mock_callback.call_count > 0


def test_window_monitor_checks_system_activity():
    """Verify WindowMonitor checks is_system_active before getting active window."""
    mock_callback = MagicMock()

    with (
        patch("auto_daily.window_monitor.is_system_active") as mock_active,
        patch("auto_daily.window_monitor.get_active_window") as mock_get_window,
    ):
        mock_active.return_value = False
        mock_get_window.return_value = {"app_name": "Test", "window_title": "Title"}

        monitor = WindowMonitor(on_window_change=mock_callback)
        monitor.start(interval=0.1)
        time.sleep(0.25)
        monitor.stop()

        # Should have checked activity but never called get_active_window
        assert mock_active.called
        assert not mock_get_window.called

        # Now set to True
        mock_active.return_value = True
        mock_active.reset_mock()
        mock_get_window.reset_mock()

        monitor = WindowMonitor(on_window_change=mock_callback)
        monitor.start(interval=0.1)
        time.sleep(0.25)
        monitor.stop()

        # Should have called get_active_window
        assert mock_get_window.called
