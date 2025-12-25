"""auto-daily: macOS window context capture and daily report generator."""

import argparse
import signal
import time

__version__ = "0.1.0"

from auto_daily.window_monitor import WindowMonitor


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
    parser.add_argument(
        "--start",
        action="store_true",
        help="Start window monitoring",
    )

    args = parser.parse_args()

    if args.start:
        print(f"auto-daily v{__version__} - Starting window monitor...")

        def on_window_change(old_window: dict, new_window: dict) -> None:
            print(f"Window changed: {old_window} -> {new_window}")

        monitor = WindowMonitor(on_window_change)
        monitor.start()

        # Handle graceful shutdown
        def signal_handler(sig: int, frame: object) -> None:
            print("\nStopping monitor...")
            monitor.stop()
            raise SystemExit(0)

        signal.signal(signal.SIGINT, signal_handler)

        # Keep main thread alive
        while True:
            time.sleep(1)
    else:
        print(f"auto-daily v{__version__}")
