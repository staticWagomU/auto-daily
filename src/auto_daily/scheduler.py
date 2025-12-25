"""Periodic capture scheduler module."""

import threading
from collections.abc import Callable
from datetime import datetime
from pathlib import Path

from auto_daily.capture import capture_screen, cleanup_image
from auto_daily.config import get_capture_interval
from auto_daily.logger import append_log
from auto_daily.ocr import perform_ocr
from auto_daily.system import is_system_active
from auto_daily.window_monitor import get_active_window

type CaptureCallback = Callable[[Path], None]
type SummaryCallback = Callable[[Path, Path], None]


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
        interval: float | None = None,
    ) -> None:
        """Initialize the periodic capture scheduler.

        Args:
            callback: Function to call on each capture interval.
            log_dir: Directory for storing logs.
            interval: Time in seconds between captures.
                     Uses AUTO_DAILY_CAPTURE_INTERVAL env var or default if not specified.
        """
        self._callback = callback
        self._log_dir = log_dir
        self._interval = (
            interval if interval is not None else float(get_capture_interval())
        )
        self._running = False
        self._thread: threading.Thread | None = None

    def _capture_loop(self) -> None:
        """Background loop that triggers captures at regular intervals."""
        while self._running:
            if is_system_active():
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


class HourlySummaryScheduler:
    """Schedule hourly log summarization.

    This scheduler triggers a callback at the top of each hour to summarize
    the previous hour's logs.
    """

    def __init__(
        self,
        callback: SummaryCallback,
        log_dir: Path,
        summaries_dir: Path,
        check_interval: float = 60.0,
    ) -> None:
        """Initialize the hourly summary scheduler.

        Args:
            callback: Function to call when summarization is needed.
                     Receives (log_dir, summaries_dir) as arguments.
            log_dir: Directory containing activity logs.
            summaries_dir: Directory for storing summaries.
            check_interval: How often to check if summarization is needed (seconds).
        """
        self._callback = callback
        self._log_dir = log_dir
        self._summaries_dir = summaries_dir
        self._check_interval = check_interval
        self._running = False
        self._thread: threading.Thread | None = None
        self._trigger_event = threading.Event()
        self._last_triggered_hour: int | None = None

    def _summary_loop(self) -> None:
        """Background loop that checks for summary triggers."""
        while self._running:
            # Wait for trigger or check interval
            triggered = self._trigger_event.wait(timeout=self._check_interval)
            if triggered:
                self._trigger_event.clear()
                self._callback(self._log_dir, self._summaries_dir)
            elif self._running:
                # Auto-trigger at top of hour
                now = datetime.now()
                current_hour = now.hour

                # Trigger at the start of a new hour (minute < 5 to give some buffer)
                if now.minute < 5 and self._last_triggered_hour != current_hour:
                    self._last_triggered_hour = current_hour
                    self._callback(self._log_dir, self._summaries_dir)

    def start(self) -> None:
        """Start the hourly summary scheduler."""
        if self._running:
            return

        self._running = True
        self._thread = threading.Thread(target=self._summary_loop)
        self._thread.daemon = True
        self._thread.start()

    def stop(self) -> None:
        """Stop the hourly summary scheduler."""
        self._running = False
        self._trigger_event.set()  # Wake up the thread
        if self._thread is not None:
            self._thread.join(timeout=1.0)
            self._thread = None

    def trigger_summary(self) -> None:
        """Manually trigger a summary generation."""
        self._trigger_event.set()
