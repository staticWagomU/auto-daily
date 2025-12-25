"""auto-daily: macOS window context capture and daily report generator."""

import argparse
import asyncio
import json
import signal
import sys
import time
from datetime import date, datetime, timedelta
from pathlib import Path

__version__ = "0.1.0"

from auto_daily.calendar import (
    LogEntry,
    get_all_events,
    match_events_with_logs,
)
from auto_daily.config import (
    get_log_dir,
    get_ollama_base_url,
    get_ollama_model,
    get_reports_dir,
    get_summaries_dir,
    load_env,
)
from auto_daily.llm.ollama import check_ollama_connection
from auto_daily.logger import get_log_filename
from auto_daily.ollama import (
    OllamaClient,
    generate_daily_report_prompt,
    generate_daily_report_prompt_with_calendar,
    save_daily_report,
)
from auto_daily.permissions import check_all_permissions
from auto_daily.processor import process_window_change
from auto_daily.scheduler import (
    HourlySummaryScheduler,
    PeriodicCapture,
    process_periodic_capture,
)
from auto_daily.summarize import (
    generate_daily_report_prompt_from_summaries,
    get_missing_summary_hours,
    get_summaries_for_date,
    save_summary,
)
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


def _load_logs_as_entries(log_file: Path) -> list[LogEntry]:
    """Load JSONL log file and convert to LogEntry objects.

    Args:
        log_file: Path to the JSONL log file.

    Returns:
        List of LogEntry objects.
    """
    entries = []
    with open(log_file) as f:
        for line in f:
            line = line.strip()
            if line:
                data = json.loads(line)
                timestamp_str = data.get("timestamp", "")
                window_info = data.get("window_info", {})
                entries.append(
                    LogEntry(
                        timestamp=datetime.fromisoformat(timestamp_str),
                        app_name=window_info.get("app_name", ""),
                        window_title=window_info.get("window_title", ""),
                        ocr_text=data.get("ocr_text", ""),
                    )
                )
    return entries


async def report_command(
    date_str: str | None = None,
    with_calendar: bool = False,
    auto_summarize: bool = False,
) -> None:
    """Generate a daily report from summaries or logs.

    Args:
        date_str: Optional date string in YYYY-MM-DD format.
                  If None, uses today's date.
        with_calendar: If True, include calendar events in report.
        auto_summarize: If True, automatically generate missing summaries.
    """
    from auto_daily.logger import get_hourly_log_filename, get_log_dir_for_date

    # Check Ollama connection before proceeding
    if not check_ollama_connection():
        ollama_url = get_ollama_base_url()
        print(
            f"Error: Cannot connect to Ollama at {ollama_url}. "
            "Please ensure Ollama is running."
        )
        sys.exit(1)

    # Determine the target date
    if date_str:
        target_date = date.fromisoformat(date_str)
    else:
        target_date = date.today()

    log_dir = get_log_dir()
    summaries_dir = get_summaries_dir()

    # Auto-summarize if requested
    if auto_summarize:
        missing_hours = get_missing_summary_hours(log_dir, summaries_dir, target_date)
        if missing_hours:
            print(f"Generating summaries for hours: {missing_hours}...")
            client = OllamaClient()
            model = get_ollama_model()

            for hour in missing_hours:
                # Read log file for this hour
                target_datetime = datetime.combine(
                    target_date, datetime.min.time()
                ).replace(hour=hour)
                date_log_dir = get_log_dir_for_date(log_dir, target_datetime)
                log_file = date_log_dir / get_hourly_log_filename(target_datetime)

                if log_file.exists():
                    log_content = log_file.read_text()
                    prompt = generate_summary_prompt(log_content)
                    summary = await client.generate(model=model, prompt=prompt)
                    save_summary(summaries_dir, target_date, hour, summary)
                    print(f"  Generated summary for hour {hour:02d}")

    # Try to use summary files first
    summaries = get_summaries_for_date(summaries_dir, target_date)

    if summaries:
        # Use summaries for report generation
        print(f"Generating report for {target_date.isoformat()} from summaries...")
        prompt = generate_daily_report_prompt_from_summaries(summaries)
    else:
        # Fall back to log file
        target_datetime = datetime.combine(target_date, datetime.min.time())
        log_file = log_dir / get_log_filename(target_datetime)

        if not log_file.exists():
            print(f"Error: No log file found for {target_date.isoformat()}")
            print(f"Expected: {log_file}")
            sys.exit(1)

        # Generate report using Ollama
        print(f"Generating report for {target_date.isoformat()}...")

        if with_calendar:
            # Fetch calendar events and match with logs
            events = await get_all_events(target_date)
            log_entries = _load_logs_as_entries(log_file)
            match_result = match_events_with_logs(events, log_entries)
            prompt = generate_daily_report_prompt_with_calendar(log_file, match_result)
        else:
            prompt = generate_daily_report_prompt(log_file)

    client = OllamaClient()
    model = get_ollama_model()
    content = await client.generate(model=model, prompt=prompt)

    # Save report
    reports_dir = get_reports_dir()
    report_path = save_daily_report(reports_dir, content, target_date)

    print(f"Report saved: {report_path}")


def generate_summary_prompt(log_content: str) -> str:
    """Generate a prompt for hourly log summarization.

    Args:
        log_content: The log content to summarize.

    Returns:
        A prompt for the LLM.
    """
    return f"""以下の1時間分のアクティビティログを簡潔に要約してください。
重要なタスク、作業内容、成果を箇条書きで記載してください。

{log_content}

要約:"""


async def summarize_command(
    date_str: str | None = None, hour: int | None = None
) -> None:
    """Generate a summary for an hour's worth of logs.

    Args:
        date_str: Optional date string in YYYY-MM-DD format.
                  If None, uses today's date.
        hour: Optional hour (0-23) to summarize.
              If None, uses the current hour.
    """
    from auto_daily.logger import get_log_dir_for_date

    # Check Ollama connection before proceeding
    if not check_ollama_connection():
        ollama_url = get_ollama_base_url()
        print(
            f"Error: Cannot connect to Ollama at {ollama_url}. "
            "Please ensure Ollama is running."
        )
        sys.exit(1)

    # Determine the target date and hour
    now = datetime.now()
    if date_str:
        target_date = date.fromisoformat(date_str)
    else:
        target_date = now.date()

    if hour is not None:
        target_hour = hour
    else:
        target_hour = now.hour

    # Get log file path
    log_dir = get_log_dir()
    target_datetime = datetime.combine(
        target_date, datetime.min.time().replace(hour=target_hour)
    )
    date_log_dir = get_log_dir_for_date(log_dir, target_datetime)
    log_file = date_log_dir / get_log_filename(target_datetime)

    if not log_file.exists():
        print(f"No log file found for {target_date.isoformat()} hour {target_hour:02d}")
        print(f"Expected: {log_file}")
        return

    # Read log content
    log_content = log_file.read_text()

    # Generate summary using Ollama
    print(f"Generating summary for {target_date.isoformat()} {target_hour:02d}:00...")

    prompt = generate_summary_prompt(log_content)
    client = OllamaClient()
    model = get_ollama_model()
    summary = await client.generate(model=model, prompt=prompt)

    # Save summary
    summaries_dir = get_summaries_dir()
    summary_path = save_summary(summaries_dir, target_date, target_hour, summary)

    print(f"Summary saved: {summary_path}")


def main() -> None:
    """Main entry point for auto-daily."""
    # Load environment variables from .env file
    load_env()

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
    report_parser.add_argument(
        "--with-calendar",
        action="store_true",
        help="Include calendar events in the report",
    )
    report_parser.add_argument(
        "--auto-summarize",
        action="store_true",
        help="Automatically generate missing summaries before report",
    )

    # Summarize subcommand
    summarize_parser = subparsers.add_parser(
        "summarize",
        help="Generate an hourly summary from logs",
    )
    summarize_parser.add_argument(
        "--date",
        type=str,
        help="Date to summarize (YYYY-MM-DD format)",
    )
    summarize_parser.add_argument(
        "--hour",
        type=int,
        help="Hour to summarize (0-23)",
    )

    args = parser.parse_args()

    # Handle report subcommand
    if args.command == "report":
        asyncio.run(report_command(args.date, args.with_calendar, args.auto_summarize))
        return

    # Handle summarize subcommand
    if args.command == "summarize":
        asyncio.run(summarize_command(args.date, args.hour))
        return

    if args.start:
        print(f"auto-daily v{__version__} - Starting window monitor...")

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
    else:
        print(f"auto-daily v{__version__}")
