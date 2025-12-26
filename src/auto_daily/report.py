"""Report and summarize command implementations for auto-daily."""

import asyncio
import json
import sys
from datetime import date, datetime
from pathlib import Path

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
    get_summary_prompt_template,
)
from auto_daily.llm.ollama import check_ollama_connection
from auto_daily.logger import get_log_filename
from auto_daily.ollama import (
    OllamaClient,
    generate_daily_report_prompt,
    generate_daily_report_prompt_with_calendar,
    save_daily_report,
)
from auto_daily.summarize import (
    generate_daily_report_prompt_from_summaries,
    get_missing_summary_hours,
    get_summaries_for_date,
    save_summary,
)


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


def generate_summary_prompt(log_content: str) -> str:
    """Generate a prompt for hourly log summarization.

    Reads template from summary_prompt.txt in project root.
    Falls back to default template if file doesn't exist.

    Args:
        log_content: The log content to summarize.

    Returns:
        A prompt for the LLM with {log_content} replaced.
    """
    template = get_summary_prompt_template()
    return template.format(log_content=log_content)


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


def run_report_command(
    date_str: str | None = None,
    with_calendar: bool = False,
    auto_summarize: bool = False,
) -> None:
    """Run report command synchronously (wrapper for CLI).

    Args:
        date_str: Optional date string in YYYY-MM-DD format.
        with_calendar: If True, include calendar events in report.
        auto_summarize: If True, automatically generate missing summaries.
    """
    asyncio.run(report_command(date_str, with_calendar, auto_summarize))


def run_summarize_command(date_str: str | None = None, hour: int | None = None) -> None:
    """Run summarize command synchronously (wrapper for CLI).

    Args:
        date_str: Optional date string in YYYY-MM-DD format.
        hour: Optional hour (0-23) to summarize.
    """
    asyncio.run(summarize_command(date_str, hour))
