"""Tests for JSONL logging functionality."""

import json
from pathlib import Path

from auto_daily.logger import append_log


def test_jsonl_append(tmp_path: Path) -> None:
    """Test that append_log writes window info, OCR text, and timestamp to JSONL.

    The function should:
    1. Create a JSONL file if it doesn't exist
    2. Append a JSON object with window_name, ocr_text, and timestamp
    3. Each call adds a new line to the file
    """
    log_dir = tmp_path / "logs"
    log_dir.mkdir()

    # Arrange
    window_info = {"app_name": "Claude Code", "window_title": "auto-daily"}
    ocr_text = "This is some OCR text from the screen"

    # Act
    log_path = append_log(
        log_dir=log_dir,
        window_info=window_info,
        ocr_text=ocr_text,
    )

    # Assert
    assert log_path is not None
    assert Path(log_path).exists()
    assert Path(log_path).suffix == ".jsonl"

    # Read and verify the log entry
    with open(log_path) as f:
        lines = f.readlines()

    assert len(lines) == 1
    entry = json.loads(lines[0])

    assert entry["window_info"] == window_info
    assert entry["ocr_text"] == ocr_text
    assert "timestamp" in entry

    # Append another entry
    window_info2 = {"app_name": "Terminal", "window_title": "zsh"}
    ocr_text2 = "Another OCR result"

    append_log(log_dir=log_dir, window_info=window_info2, ocr_text=ocr_text2)

    with open(log_path) as f:
        lines = f.readlines()

    assert len(lines) == 2
