"""Ollama API integration for daily report generation."""

import json
from datetime import date
from pathlib import Path

import httpx

from auto_daily.config import get_prompt_template


class OllamaClient:
    """Client for interacting with the Ollama API."""

    def __init__(self, base_url: str = "http://localhost:11434") -> None:
        """Initialize the Ollama client.

        Args:
            base_url: Base URL of the Ollama server.
        """
        self.base_url = base_url

    async def generate(self, model: str, prompt: str) -> str:
        """Generate text using the Ollama API.

        Args:
            model: Name of the model to use.
            prompt: The prompt to send to the model.

        Returns:
            Generated text response.
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False,
                },
                timeout=120.0,
            )
            response.raise_for_status()
            return response.json()["response"]


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
