"""JSONL logging module for activity tracking."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any


def get_log_dir_for_date(log_base: Path, dt: datetime | None = None) -> Path:
    """Get or create a date-specific log directory.

    Args:
        log_base: Base directory for logs.
        dt: Datetime to use for directory name. Defaults to now.

    Returns:
        Path to the date directory (e.g., logs/2025-12-25/).
    """
    if dt is None:
        dt = datetime.now()
    date_dir = log_base / dt.strftime("%Y-%m-%d")
    date_dir.mkdir(parents=True, exist_ok=True)
    return date_dir


def get_hourly_log_filename(dt: datetime | None = None) -> str:
    """Generate log filename based on hour.

    Args:
        dt: Datetime to use for filename. Defaults to now.

    Returns:
        Filename in format 'activity_HH.jsonl'.
    """
    if dt is None:
        dt = datetime.now()
    return f"activity_{dt.strftime('%H')}.jsonl"


def get_log_filename(date: datetime | None = None) -> str:
    """Generate log filename based on date (legacy).

    Args:
        date: Date to use for filename. Defaults to today.

    Returns:
        Filename in format 'activity_YYYY-MM-DD.jsonl'.
    """
    if date is None:
        date = datetime.now()
    return f"activity_{date.strftime('%Y-%m-%d')}.jsonl"


def append_log_hourly(
    log_base: Path,
    window_info: dict[str, str],
    ocr_text: str,
    *,
    slack_context: Any = None,
) -> Path | None:
    """Append an activity log entry to the hourly JSONL file.

    Args:
        log_base: Base directory for logs.
        window_info: Dictionary with app_name and window_title.
        ocr_text: OCR extracted text from the screen.
        slack_context: Optional Slack context with channel, workspace, dm_user, is_thread.

    Returns:
        Path to the log file, or None if logging failed.
    """
    try:
        now = datetime.now()
        date_dir = get_log_dir_for_date(log_base, now)
        log_path = date_dir / get_hourly_log_filename(now)

        entry: dict[str, Any] = {
            "timestamp": now.isoformat(),
            "window_info": window_info,
            "ocr_text": ocr_text,
            "slack_context": slack_context,
        }

        with open(log_path, "a") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

        return log_path
    except OSError:
        return None
