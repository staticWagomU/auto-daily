"""Ollama API integration for daily report generation.

This module provides utility functions for generating daily reports.
The OllamaClient class is now located in auto_daily.llm.ollama but is
re-exported here for backward compatibility.
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import TYPE_CHECKING

from auto_daily.config import get_prompt_template

# Re-export OllamaClient for backward compatibility
from auto_daily.llm.ollama import OllamaClient

if TYPE_CHECKING:
    from auto_daily.calendar import MatchResult

__all__ = [
    "OllamaClient",
    "generate_daily_report_prompt",
    "generate_daily_report_prompt_with_calendar",
    "save_daily_report",
]


def generate_daily_report_prompt(log_file: Path) -> str:
    """Generate a prompt for daily report from JSONL log file.

    Args:
        log_file: Path to the JSONL log file.

    Returns:
        Formatted prompt for LLM to generate daily report.
    """
    entries = []
    with open(log_file) as f:
        for line in f:
            line = line.strip()
            if line:
                entries.append(json.loads(line))

    # Format activity entries
    activity_lines = []
    for entry in entries:
        timestamp = entry.get("timestamp", "不明")
        window_info = entry.get("window_info", {})
        app_name = window_info.get("app_name", "不明")
        window_title = window_info.get("window_title", "")
        ocr_text = entry.get("ocr_text", "")

        activity_lines.append(
            f"- {timestamp}: {app_name} ({window_title})\n  内容: {ocr_text[:100]}..."
            if len(ocr_text) > 100
            else f"- {timestamp}: {app_name} ({window_title})\n  内容: {ocr_text}"
        )

    activities = "\n".join(activity_lines)

    # Use template from config
    template = get_prompt_template()
    prompt = template.format(activities=activities)

    return prompt


def generate_daily_report_prompt_with_calendar(
    log_file: Path, match_result: MatchResult
) -> str:
    """Generate a prompt for daily report with calendar information.

    Args:
        log_file: Path to the JSONL log file.
        match_result: Result from matching calendar events with logs.

    Returns:
        Formatted prompt for LLM with calendar and activity information.
    """
    # Load log entries
    entries = []
    with open(log_file) as f:
        for line in f:
            line = line.strip()
            if line:
                entries.append(json.loads(line))

    # Format activity entries
    activity_lines = []
    for entry in entries:
        timestamp = entry.get("timestamp", "不明")
        window_info = entry.get("window_info", {})
        app_name = window_info.get("app_name", "不明")
        window_title = window_info.get("window_title", "")
        ocr_text = entry.get("ocr_text", "")

        activity_lines.append(
            f"- {timestamp}: {app_name} ({window_title})\n  内容: {ocr_text[:100]}..."
            if len(ocr_text) > 100
            else f"- {timestamp}: {app_name} ({window_title})\n  内容: {ocr_text}"
        )

    activities = "\n".join(activity_lines)

    # Format calendar sections
    schedule_lines = []
    completed_lines = []
    unstarted_lines = []
    unplanned_lines = []

    # Matched events (completed as planned)
    for event, logs in match_result.matched:
        start_time = event.start.strftime("%H:%M")
        end_time = event.end.strftime("%H:%M")
        schedule_lines.append(f"- {start_time}-{end_time}: {event.summary}")
        completed_lines.append(
            f"- {start_time}-{end_time}: {event.summary}（ログ {len(logs)} 件）"
        )

    # Unstarted events
    for event in match_result.unstarted:
        start_time = event.start.strftime("%H:%M")
        end_time = event.end.strftime("%H:%M")
        schedule_lines.append(f"- {start_time}-{end_time}: {event.summary}")
        unstarted_lines.append(
            f"- {start_time}-{end_time}: {event.summary}（ログなし）"
        )

    # Unplanned work
    for log in match_result.unplanned:
        log_time = log.timestamp.strftime("%H:%M")
        unplanned_lines.append(f"- {log_time}: {log.app_name} - {log.window_title}")

    # Build prompt with calendar context
    schedule_section = "\n".join(schedule_lines) if schedule_lines else "予定なし"
    completed_section = "\n".join(completed_lines) if completed_lines else "該当なし"
    unstarted_section = "\n".join(unstarted_lines) if unstarted_lines else "該当なし"
    unplanned_section = "\n".join(unplanned_lines) if unplanned_lines else "該当なし"

    prompt = f"""以下の情報をもとに日報を作成してください。
予定と実績の差分についてもコメントしてください。

## 今日の予定
{schedule_section}

## アクティビティログ
{activities}

## 予定と実績の照合

### 予定通り実施
{completed_section}

### 未着手の予定
{unstarted_section}

### 予定外の作業
{unplanned_section}

## 日報フォーマット
1. 今日の作業内容
2. 進捗・成果
3. 課題・問題点
4. 明日の予定
"""

    return prompt


def save_daily_report(output_dir: Path, content: str, report_date: date) -> Path:
    """Save the daily report to a Markdown file.

    Args:
        output_dir: Directory to save the report.
        content: Report content to save.
        report_date: Date of the report for filename.

    Returns:
        Path to the saved report file.
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    filename = f"daily_report_{report_date.isoformat()}.md"
    file_path = output_dir / filename

    file_path.write_text(content)

    return file_path
