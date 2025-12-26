"""Window monitoring and scheduling for auto-daily."""

import asyncio
import signal
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

from auto_daily.config import (
    get_log_dir,
    get_ollama_base_url,
    get_ollama_model,
    get_summaries_dir,
)
from auto_daily.llm.ollama import check_ollama_connection
from auto_daily.ollama import OllamaClient
from auto_daily.permissions import check_all_permissions
from auto_daily.processor import process_window_change
from auto_daily.report import generate_summary_prompt
from auto_daily.scheduler import (
    HourlySummaryScheduler,
    PeriodicCapture,
    process_periodic_capture,
)
from auto_daily.summarize import save_summary
from auto_daily.window_monitor import WindowMonitor

# Default interval for periodic capture (30 seconds)
PERIODIC_CAPTURE_INTERVAL = 30.0

# Default interval for hourly summary check (60 seconds)
HOURLY_SUMMARY_CHECK_INTERVAL = 60.0


def on_periodic_capture(log_dir: Path) -> None:
    """Callback for periodic capture events."""
    success = process_periodic_capture(log_dir)
    if success:
        print("⏱ Periodic capture: ✓ Captured, OCR'd, and logged")
    else:
        print("⏱ Periodic capture: ✗ Processing failed")


def on_hourly_summary(log_dir: Path, summaries_dir: Path) -> None:
    """Callback for hourly summary generation.

    Summarizes the previous hour's logs if not already summarized.
    """
    from auto_daily.logger import get_hourly_log_filename, get_log_dir_for_date

    now = datetime.now()
    # Summarize the previous hour
    prev_hour = (now.hour - 1) % 24
    target_date = now.date() if now.hour > 0 else (now - timedelta(days=1)).date()

    # Check if summary already exists
    summary_date_dir = summaries_dir / target_date.isoformat()
    summary_file = summary_date_dir / f"summary_{prev_hour:02d}.md"

    if summary_file.exists():
        return  # Already summarized

    # Check if log file exists for this hour
    target_datetime = datetime.combine(target_date, datetime.min.time()).replace(
        hour=prev_hour
    )
    date_log_dir = get_log_dir_for_date(log_dir, target_datetime)
    log_file = date_log_dir / get_hourly_log_filename(target_datetime)

    if not log_file.exists():
        return  # No log to summarize

    # Check Ollama connection
    if not check_ollama_connection():
        print(f"⚠️ Cannot summarize hour {prev_hour:02d}: Ollama not available")
        return

    # Generate summary
    print(f"📝 Generating summary for {target_date.isoformat()} {prev_hour:02d}:00...")
    log_content = log_file.read_text()
    prompt = generate_summary_prompt(log_content)

    client = OllamaClient()
    model = get_ollama_model()

    try:
        summary = asyncio.run(client.generate(model=model, prompt=prompt))
        save_summary(summaries_dir, target_date, prev_hour, summary)
        print(f"  ✓ Summary saved: {summary_file}")
    except Exception as e:
        print(f"  ✗ Summary failed: {e}")


def start_monitoring(version: str) -> None:
    """Start window monitoring with periodic capture and hourly summary.

    Args:
        version: Version string for display.
    """
    print(f"auto-daily v{version} - Starting window monitor...")

    # Check permissions before starting
    perms = check_all_permissions()
    missing_perms = False

    if not perms["screen_recording"]:
        print("⚠️ Screen recording permission is required.")
        missing_perms = True

    if not perms["accessibility"]:
        print("⚠️ Accessibility permission is required.")
        missing_perms = True

    if missing_perms:
        print("Run: bash scripts/setup-permissions.sh")
        print("Please grant permissions and restart.")
        sys.exit(1)

    # Check Ollama connection and warn if unavailable
    if not check_ollama_connection():
        ollama_url = get_ollama_base_url()
        print(
            f"⚠️ Warning: Ollama is not available at {ollama_url}. "
            "Report generation will not work."
        )

    log_dir = get_log_dir()
    summaries_dir = get_summaries_dir()
    print(f"Logging to: {log_dir}")
    print(f"Summaries to: {summaries_dir}")

    def on_window_change(old_window: dict, new_window: dict) -> None:
        print(f"Window changed: {old_window['app_name']} -> {new_window['app_name']}")
        success = process_window_change(old_window, new_window, log_dir)
        if success:
            print("  ✓ Captured, OCR'd, and logged")
        else:
            print("  ✗ Processing failed")

    # Start window change monitor
    monitor = WindowMonitor(on_window_change)
    monitor.start()

    # Start periodic capture scheduler (every 30 seconds)
    periodic = PeriodicCapture(
        callback=on_periodic_capture,
        log_dir=log_dir,
        interval=PERIODIC_CAPTURE_INTERVAL,
    )
    periodic.start()
    print(f"Periodic capture: every {PERIODIC_CAPTURE_INTERVAL:.0f} seconds")

    # Start hourly summary scheduler
    hourly_summary = HourlySummaryScheduler(
        callback=on_hourly_summary,
        log_dir=log_dir,
        summaries_dir=summaries_dir,
        check_interval=HOURLY_SUMMARY_CHECK_INTERVAL,
    )
    hourly_summary.start()
    print("Hourly summary: enabled (auto-summarize every hour)")

    # Handle graceful shutdown
    def signal_handler(sig: int, frame: object) -> None:
        print("\nStopping...")
        monitor.stop()
        periodic.stop()
        hourly_summary.stop()
        raise SystemExit(0)

    signal.signal(signal.SIGINT, signal_handler)

    # Keep main thread alive
    while True:
        time.sleep(1)
