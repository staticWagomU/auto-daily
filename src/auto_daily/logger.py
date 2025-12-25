"""JSONL logging module for activity tracking."""

import json
from datetime import datetime
from pathlib import Path


def get_log_filename(date: datetime | None = None) -> str:
    """Generate log filename based on date.

    Args:
        date: Date to use for filename. Defaults to today.

    Returns:
        Filename in format 'activity_YYYY-MM-DD.jsonl'.
    """
    if date is None:
        date = datetime.now()
    return f"activity_{date.strftime('%Y-%m-%d')}.jsonl"


def append_log(
    log_dir: Path,
    window_info: dict[str, str],
    ocr_text: str,
) -> str | None:
    """Append an activity log entry to the JSONL file.

    Args:
        log_dir: Directory where log files are stored.
        window_info: Dictionary with app_name and window_title.
        ocr_text: OCR extracted text from the screen.

    Returns:
        Path to the log file, or None if logging failed.
    """
    try:
        log_path = log_dir / get_log_filename()

        entry = {
            "timestamp": datetime.now().isoformat(),
            "window_info": window_info,
            "ocr_text": ocr_text,
        }

        with open(log_path, "a") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

        return str(log_path)
    except OSError:
        return None
