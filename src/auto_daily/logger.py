"""JSONL logging module for activity tracking."""

from pathlib import Path


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
    raise NotImplementedError("append_log is not yet implemented")
