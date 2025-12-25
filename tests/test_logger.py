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


def test_daily_rotation(tmp_path: Path) -> None:
    """Test that JSONL files are rotated daily based on date.

    The function should:
    1. Use different filenames for different dates
    2. Filename format should be 'activity_YYYY-MM-DD.jsonl'
    3. Logs from different days go to different files
    """
    from datetime import datetime

    from auto_daily.logger import get_log_filename

    # Act
    today = datetime(2024, 12, 25)
    tomorrow = datetime(2024, 12, 26)
    next_year = datetime(2025, 1, 1)

    today_filename = get_log_filename(today)
    tomorrow_filename = get_log_filename(tomorrow)
    next_year_filename = get_log_filename(next_year)

    # Assert
    assert today_filename == "activity_2024-12-25.jsonl"
    assert tomorrow_filename == "activity_2024-12-26.jsonl"
    assert next_year_filename == "activity_2025-01-01.jsonl"

    # All filenames should be different
    assert today_filename != tomorrow_filename
    assert today_filename != next_year_filename
    assert tomorrow_filename != next_year_filename


def test_date_directory_creation(tmp_path: Path) -> None:
    """Test that date directory logs/YYYY-MM-DD/ is automatically created.

    The function should:
    1. Create a date directory if it doesn't exist
    2. Directory format should be 'YYYY-MM-DD'
    3. Return the path to the date directory
    """
    from datetime import datetime

    from auto_daily.logger import get_log_dir_for_date

    log_base = tmp_path / "logs"
    log_base.mkdir()

    # Act
    dt = datetime(2025, 12, 25, 10, 30, 0)
    date_dir = get_log_dir_for_date(log_base, dt)

    # Assert
    assert date_dir == log_base / "2025-12-25"
    assert date_dir.exists()
    assert date_dir.is_dir()


def test_hourly_log_filename() -> None:
    """Test that log filename is generated in activity_HH.jsonl format.

    The function should:
    1. Generate filename based on hour
    2. Filename format should be 'activity_HH.jsonl'
    3. Different hours produce different filenames
    """
    from datetime import datetime

    from auto_daily.logger import get_hourly_log_filename

    # Act
    morning = datetime(2025, 12, 25, 9, 30, 0)
    noon = datetime(2025, 12, 25, 12, 0, 0)
    evening = datetime(2025, 12, 25, 18, 45, 0)

    morning_filename = get_hourly_log_filename(morning)
    noon_filename = get_hourly_log_filename(noon)
    evening_filename = get_hourly_log_filename(evening)

    # Assert
    assert morning_filename == "activity_09.jsonl"
    assert noon_filename == "activity_12.jsonl"
    assert evening_filename == "activity_18.jsonl"

    # All filenames should be different
    assert morning_filename != noon_filename
    assert morning_filename != evening_filename
    assert noon_filename != evening_filename


def test_hourly_rotation(tmp_path: Path) -> None:
    """Test that logs are written to different files when hour changes.

    The function should:
    1. Write to a different file when the hour changes
    2. Create date directory and hourly log file automatically
    3. Both files should exist with correct entries
    """
    from datetime import datetime
    from unittest.mock import patch

    from auto_daily.logger import append_log_hourly

    log_base = tmp_path / "logs"
    log_base.mkdir()

    window_info = {"app_name": "Test App", "window_title": "Test Window"}
    ocr_text = "Test OCR text"

    # Arrange - mock datetime for 09:30
    with patch("auto_daily.logger.datetime") as mock_dt:
        mock_dt.now.return_value = datetime(2025, 12, 25, 9, 30, 0)
        mock_dt.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)

        # Act - write log at 09:30
        log_path_09 = append_log_hourly(
            log_base=log_base,
            window_info=window_info,
            ocr_text=ocr_text,
        )

    # Assert - log written to 2025-12-25/activity_09.jsonl
    assert log_path_09 is not None
    expected_path_09 = log_base / "2025-12-25" / "activity_09.jsonl"
    assert Path(log_path_09) == expected_path_09
    assert expected_path_09.exists()

    # Arrange - mock datetime for 10:15
    with patch("auto_daily.logger.datetime") as mock_dt:
        mock_dt.now.return_value = datetime(2025, 12, 25, 10, 15, 0)
        mock_dt.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)

        # Act - write log at 10:15
        log_path_10 = append_log_hourly(
            log_base=log_base,
            window_info=window_info,
            ocr_text="Different OCR text",
        )

    # Assert - log written to 2025-12-25/activity_10.jsonl
    assert log_path_10 is not None
    expected_path_10 = log_base / "2025-12-25" / "activity_10.jsonl"
    assert Path(log_path_10) == expected_path_10
    assert expected_path_10.exists()

    # Both files should exist and be different
    assert log_path_09 != log_path_10


def test_legacy_daily_log_compat(tmp_path: Path) -> None:
    """Test backward compatibility with existing daily log format.

    The legacy append_log function should:
    1. Continue to work with the existing daily format (activity_YYYY-MM-DD.jsonl)
    2. Not break existing functionality during migration period
    3. Allow both legacy and hourly logging to coexist
    """
    import json

    from auto_daily.logger import append_log, append_log_hourly

    log_base = tmp_path / "logs"
    log_base.mkdir()

    window_info = {"app_name": "Test App", "window_title": "Test Window"}
    ocr_text = "Test OCR text"

    # Act - use legacy daily log
    legacy_path = append_log(
        log_dir=log_base,
        window_info=window_info,
        ocr_text=ocr_text,
    )

    # Assert - legacy log should work
    assert legacy_path is not None
    assert Path(legacy_path).exists()
    # Legacy filename format: activity_YYYY-MM-DD.jsonl
    assert "activity_" in Path(legacy_path).name
    assert Path(legacy_path).suffix == ".jsonl"

    # Verify content
    with open(legacy_path) as f:
        entry = json.loads(f.readline())
    assert entry["window_info"] == window_info
    assert entry["ocr_text"] == ocr_text
    assert "timestamp" in entry

    # Act - use hourly log (should work alongside legacy)
    date_dir = log_base / "2025-12-25"
    date_dir.mkdir(exist_ok=True)
    hourly_path = append_log_hourly(
        log_base=log_base,
        window_info=window_info,
        ocr_text="Hourly OCR text",
    )

    # Assert - both systems coexist
    assert hourly_path is not None
    assert hourly_path.exists()
    assert Path(legacy_path).exists()  # Legacy still exists
