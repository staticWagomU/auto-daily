"""Summarize module for hourly log summarization (PBI-026)."""

from datetime import date
from pathlib import Path


def get_summary_dir_for_date(summaries_base: Path, target_date: date) -> Path:
    """Get the summary directory path for a specific date.

    Creates the directory if it doesn't exist.

    Args:
        summaries_base: Base directory for summaries.
        target_date: The date for which to get the summary directory.

    Returns:
        Path to the summary directory (summaries/YYYY-MM-DD/).
    """
    date_dir = summaries_base / target_date.strftime("%Y-%m-%d")
    date_dir.mkdir(parents=True, exist_ok=True)
    return date_dir


def get_summary_filename(hour: int) -> str:
    """Get the summary filename for a specific hour.

    Args:
        hour: The hour (0-23) for which to get the filename.

    Returns:
        Filename in summary_HH.md format.
    """
    return f"summary_{hour:02d}.md"


def save_summary(
    summaries_base: Path, target_date: date, hour: int, content: str
) -> Path:
    """Save a summary to the appropriate file.

    Args:
        summaries_base: Base directory for summaries.
        target_date: The date of the summary.
        hour: The hour (0-23) of the summary.
        content: The summary content to save.

    Returns:
        Path to the saved summary file.
    """
    date_dir = get_summary_dir_for_date(summaries_base, target_date)
    filename = get_summary_filename(hour)
    summary_file = date_dir / filename
    summary_file.write_text(content)
    return summary_file
