"""auto-daily: macOS window context capture and daily report generator."""

import argparse
import asyncio
import signal
import sys
import time
from datetime import date, datetime
from pathlib import Path

__version__ = "0.1.0"

from auto_daily.config import get_log_dir, get_ollama_model, get_reports_dir
from auto_daily.logger import get_log_filename
from auto_daily.ollama import (
    OllamaClient,
    generate_daily_report_prompt,
    save_daily_report,
)
from auto_daily.processor import process_window_change
from auto_daily.scheduler import PeriodicCapture, process_periodic_capture
from auto_daily.window_monitor import WindowMonitor

# Default interval for periodic capture (30 seconds)
PERIODIC_CAPTURE_INTERVAL = 30.0


def on_periodic_capture(log_dir: Path) -> None:
    """Callback for periodic capture events."""
    success = process_periodic_capture(log_dir)
    if success:
        print("⏱ Periodic capture: ✓ Captured, OCR'd, and logged")
    else:
        print("⏱ Periodic capture: ✗ Processing failed")


async def report_command(date_str: str | None = None) -> None:
    """Generate a daily report from logs.

    Args:
        date_str: Optional date string in YYYY-MM-DD format.
                  If None, uses today's date.
    """
    # Determine the target date
    if date_str:
        target_date = date.fromisoformat(date_str)
    else:
        target_date = date.today()

    # Get log file path using the same format as logger.py
    log_dir = get_log_dir()
    target_datetime = datetime.combine(target_date, datetime.min.time())
    log_file = log_dir / get_log_filename(target_datetime)

    if not log_file.exists():
        print(f"Error: No log file found for {target_date.isoformat()}")
        print(f"Expected: {log_file}")
        sys.exit(1)

    # Generate report using Ollama
    print(f"Generating report for {target_date.isoformat()}...")
    prompt = generate_daily_report_prompt(log_file)

    client = OllamaClient()
    model = get_ollama_model()
    content = await client.generate(model=model, prompt=prompt)

    # Save report
    reports_dir = get_reports_dir()
    report_path = save_daily_report(reports_dir, content, target_date)

    print(f"Report saved: {report_path}")


def main() -> None:
    """Main entry point for auto-daily."""
    parser = argparse.ArgumentParser(
        prog="auto-daily",
        description="macOS window context capture and daily report generator",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    subparsers = parser.add_subparsers(dest="command")

    # Start command (legacy --start flag support)
    parser.add_argument(
        "--start",
        action="store_true",
        help="Start window monitoring",
    )

    # Report subcommand
    report_parser = subparsers.add_parser(
        "report",
        help="Generate a daily report from logs",
    )
    report_parser.add_argument(
        "--date",
        type=str,
        help="Date to generate report for (YYYY-MM-DD format)",
    )

    args = parser.parse_args()

    # Handle report subcommand
    if args.command == "report":
        asyncio.run(report_command(args.date))
        return

    if args.start:
        print(f"auto-daily v{__version__} - Starting window monitor...")

        log_dir = get_log_dir()
        print(f"Logging to: {log_dir}")

        def on_window_change(old_window: dict, new_window: dict) -> None:
            print(
                f"Window changed: {old_window['app_name']} -> {new_window['app_name']}"
            )
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

        # Handle graceful shutdown
        def signal_handler(sig: int, frame: object) -> None:
            print("\nStopping...")
            monitor.stop()
            periodic.stop()
            raise SystemExit(0)

        signal.signal(signal.SIGINT, signal_handler)

        # Keep main thread alive
        while True:
            time.sleep(1)
    else:
        print(f"auto-daily v{__version__}")
