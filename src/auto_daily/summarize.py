"""Summarize module for hourly log summarization (PBI-026, PBI-027)."""

import re
from datetime import date
from pathlib import Path


def get_log_hours_for_date(log_base: Path, target_date: date) -> list[int]:
    """Get all hours that have log files for a specific date.

    Args:
        log_base: Base directory for logs.
        target_date: The date for which to get log hours.

    Returns:
        List of hours (0-23) that have log files.
    """
    date_dir = log_base / target_date.strftime("%Y-%m-%d")

    if not date_dir.exists():
        return []

    hours: list[int] = []
    pattern = re.compile(r"activity_(\d{2})\.jsonl")

    for log_file in date_dir.glob("activity_*.jsonl"):
        match = pattern.match(log_file.name)
        if match:
            hours.append(int(match.group(1)))

    return sorted(hours)


def get_missing_summary_hours(
    log_base: Path, summaries_base: Path, target_date: date
) -> list[int]:
    """Get hours that have logs but no summaries.

    Args:
        log_base: Base directory for logs.
        summaries_base: Base directory for summaries.
        target_date: The date to check.

    Returns:
        List of hours that have logs but no corresponding summaries.
    """
    log_hours = set(get_log_hours_for_date(log_base, target_date))
    summaries = get_summaries_for_date(summaries_base, target_date)
    summary_hours = set(summaries.keys())

    return sorted(log_hours - summary_hours)


def get_summaries_for_date(summaries_base: Path, target_date: date) -> dict[int, str]:
    """Get all available summaries for a specific date.

    Args:
        summaries_base: Base directory for summaries.
        target_date: The date for which to get summaries.

    Returns:
        Dictionary mapping hour (0-23) to summary content.
        Only includes hours that have summary files.
    """
    date_dir = summaries_base / target_date.strftime("%Y-%m-%d")

    if not date_dir.exists():
        return {}

    summaries: dict[int, str] = {}
    pattern = re.compile(r"summary_(\d{2})\.md")

    for summary_file in date_dir.glob("summary_*.md"):
        match = pattern.match(summary_file.name)
        if match:
            hour = int(match.group(1))
            summaries[hour] = summary_file.read_text()

    return summaries


def generate_daily_report_prompt_from_summaries(summaries: dict[int, str]) -> str:
    """Generate a prompt for daily report from hourly summaries.

    Args:
        summaries: Dictionary mapping hour (0-23) to summary content.

    Returns:
        A prompt for the LLM to generate a daily report.
    """
    if not summaries:
        return ""

    # Sort by hour
    sorted_hours = sorted(summaries.keys())

    summary_sections = []
    for hour in sorted_hours:
        content = summaries[hour]
        summary_sections.append(f"## {hour:02d}:00-{hour + 1:02d}:00\n{content}")

    combined_summaries = "\n\n".join(summary_sections)

    return f"""以下は今日の作業の時間帯ごとの要約です。
これらをもとに、1日の日報を作成してください。

{combined_summaries}

## 日報フォーマット
以下の形式で日報を作成してください：

1. 今日の作業内容（箇条書き）
2. 進捗・成果
3. 課題・問題点
4. 明日の予定

日本語で簡潔に記述してください。"""


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
