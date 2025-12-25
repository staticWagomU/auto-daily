"""Periodic capture scheduler module."""

import threading
from collections.abc import Callable
from pathlib import Path

from auto_daily.capture import capture_screen, cleanup_image
from auto_daily.logger import append_log
from auto_daily.ocr import perform_ocr
from auto_daily.window_monitor import get_active_window

type CaptureCallback = Callable[[Path], None]


def process_periodic_capture(log_dir: Path) -> bool:
    """Process a periodic capture event.

    Captures the screen, performs OCR, and logs the activity.

    Args:
        log_dir: Directory for storing logs and temporary captures.

    Returns:
        True if processing completed successfully, False otherwise.
    """
    # Get current window info
    window_info = get_active_window()

    # Capture the screen
    image_path = capture_screen(log_dir)
    if image_path is None:
        return False

    # Perform OCR
    ocr_text = perform_ocr(image_path)

    # Log the activity
    append_log(log_dir, window_info, ocr_text)

    # Clean up
    cleanup_image(image_path)

    return True


class PeriodicCapture:
    """Periodically capture the screen at regular intervals."""

    def __init__(
        self,
        callback: CaptureCallback,
        log_dir: Path,
        interval: float = 30.0,
    ) -> None:
        """Initialize the periodic capture scheduler.

        Args:
            callback: Function to call on each capture interval.
            log_dir: Directory for storing logs.
            interval: Time in seconds between captures. Default is 30 seconds.
        """
        self._callback = callback
        self._log_dir = log_dir
        self._interval = interval
        self._running = False
        self._thread: threading.Thread | None = None

    def _capture_loop(self) -> None:
        """Background loop that triggers captures at regular intervals."""
        while self._running:
            self._callback(self._log_dir)
            # Use a loop with short sleeps to allow faster stop
            elapsed = 0.0
            while self._running and elapsed < self._interval:
                threading.Event().wait(0.05)
                elapsed += 0.05

    def start(self) -> None:
        """Start the periodic capture scheduler."""
        if self._running:
            return

        self._running = True
        self._thread = threading.Thread(target=self._capture_loop)
        self._thread.daemon = True
        self._thread.start()

    def stop(self) -> None:
        """Stop the periodic capture scheduler."""
        self._running = False
        if self._thread is not None:
            self._thread.join(timeout=1.0)
            self._thread = None
