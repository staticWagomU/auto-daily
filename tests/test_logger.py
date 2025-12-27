"""Tests for JSONL logging functionality."""

import json
from pathlib import Path

from auto_daily.logger import append_log_hourly


def test_jsonl_append(log_base: Path) -> None:
    """Test that append_log_hourly writes window info, OCR text, and timestamp to JSONL.

    The function should:
    1. Create a JSONL file if it doesn't exist
    2. Append a JSON object with window_name, ocr_text, and timestamp
    3. Each call adds a new line to the file
    """
    # Arrange
    window_info = {"app_name": "Claude Code", "window_title": "auto-daily"}
    ocr_text = "This is some OCR text from the screen"

    # Act
    log_path = append_log_hourly(
        log_base=log_base,
        window_info=window_info,
        ocr_text=ocr_text,
    )

    # Assert
    assert log_path is not None
    assert log_path.exists()
    assert log_path.suffix == ".jsonl"

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

    append_log_hourly(log_base=log_base, window_info=window_info2, ocr_text=ocr_text2)

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


def test_date_directory_creation(log_base: Path) -> None:
    """Test that date directory logs/YYYY-MM-DD/ is automatically created.

    The function should:
    1. Create a date directory if it doesn't exist
    2. Directory format should be 'YYYY-MM-DD'
    3. Return the path to the date directory
    """
    from datetime import datetime

    from auto_daily.logger import get_log_dir_for_date

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


def test_hourly_rotation(log_base: Path, sample_window_info: dict[str, str]) -> None:
    """Test that logs are written to different files when hour changes.

    The function should:
    1. Write to a different file when the hour changes
    2. Create date directory and hourly log file automatically
    3. Both files should exist with correct entries
    """
    from datetime import datetime
    from unittest.mock import patch

    from auto_daily.logger import append_log_hourly

    window_info = sample_window_info
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


def test_append_log_hourly_with_slack_context(log_base: Path) -> None:
    """Test that append_log_hourly supports slack_context parameter.

    When slack_context is provided to append_log_hourly:
    1. The log entry should include all Slack context fields
    2. Fields should be properly serialized as JSON
    3. Log should be saved in date directory with hourly filename
    """
    import json
    from datetime import datetime
    from unittest.mock import patch

    from auto_daily.logger import append_log_hourly

    window_info = {"app_name": "Slack", "window_title": "#dev-team | Company"}
    ocr_text = "Slack conversation text"
    slack_context = {
        "channel": "dev-team",
        "workspace": "Company",
        "dm_user": None,
        "is_thread": False,
    }

    # Act - mock datetime to control file path
    with patch("auto_daily.logger.datetime") as mock_dt:
        mock_dt.now.return_value = datetime(2025, 12, 26, 10, 30, 0)
        mock_dt.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)

        log_path = append_log_hourly(
            log_base=log_base,
            window_info=window_info,
            ocr_text=ocr_text,
            slack_context=slack_context,
        )

    # Assert
    assert log_path is not None
    expected_path = log_base / "2025-12-26" / "activity_10.jsonl"
    assert log_path == expected_path
    assert log_path.exists()

    with open(log_path) as f:
        entry = json.loads(f.readline())

    assert "slack_context" in entry
    assert entry["slack_context"]["channel"] == "dev-team"
    assert entry["slack_context"]["workspace"] == "Company"
    assert entry["slack_context"]["dm_user"] is None
    assert entry["slack_context"]["is_thread"] is False


def test_append_log_speech_basic(log_base: Path) -> None:
    """Test that append_log_speech writes speech recognition result to JSONL.

    The function should:
    1. Create a JSONL file if it doesn't exist
    2. Append a JSON object with type='speech', transcript, confidence, is_final
    3. Use the same date/hour directory structure as window logs
    """
    from datetime import datetime
    from unittest.mock import patch

    from auto_daily.logger import append_log_speech

    # Arrange
    transcript = "今日のスプリントレビューについて話しましょう"
    confidence = 0.95
    is_final = True

    # Act - mock datetime to control file path
    with patch("auto_daily.logger.datetime") as mock_dt:
        mock_dt.now.return_value = datetime(2025, 12, 27, 14, 30, 0)
        mock_dt.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)

        log_path = append_log_speech(
            log_base=log_base,
            transcript=transcript,
            confidence=confidence,
            is_final=is_final,
        )

    # Assert
    assert log_path is not None
    expected_path = log_base / "2025-12-27" / "activity_14.jsonl"
    assert log_path == expected_path
    assert log_path.exists()

    with open(log_path) as f:
        entry = json.loads(f.readline())

    assert entry["type"] == "speech"
    assert entry["transcript"] == transcript
    assert entry["confidence"] == confidence
    assert entry["is_final"] is True
    assert entry["language"] == "ja-JP"  # default language
    assert "timestamp" in entry


def test_append_log_speech_with_custom_language(log_base: Path) -> None:
    """Test that append_log_speech accepts custom language parameter.

    The function should:
    1. Accept an optional language parameter
    2. Default to 'ja-JP' if not specified
    3. Store the language in the log entry
    """
    from datetime import datetime
    from unittest.mock import patch

    from auto_daily.logger import append_log_speech

    # Arrange
    transcript = "Let's discuss the sprint review"
    confidence = 0.88
    is_final = True
    language = "en-US"

    # Act - mock datetime to control file path
    with patch("auto_daily.logger.datetime") as mock_dt:
        mock_dt.now.return_value = datetime(2025, 12, 27, 15, 0, 0)
        mock_dt.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)

        log_path = append_log_speech(
            log_base=log_base,
            transcript=transcript,
            confidence=confidence,
            is_final=is_final,
            language=language,
        )

    # Assert
    assert log_path is not None
    with open(log_path) as f:
        entry = json.loads(f.readline())

    assert entry["language"] == "en-US"


def test_append_log_speech_interim_result(log_base: Path) -> None:
    """Test that append_log_speech handles interim (non-final) recognition results.

    The function should:
    1. Accept is_final=False for interim results
    2. Store is_final correctly in the log entry
    """
    from datetime import datetime
    from unittest.mock import patch

    from auto_daily.logger import append_log_speech

    # Arrange
    transcript = "今日の"
    confidence = 0.7
    is_final = False

    # Act - mock datetime to control file path
    with patch("auto_daily.logger.datetime") as mock_dt:
        mock_dt.now.return_value = datetime(2025, 12, 27, 16, 0, 0)
        mock_dt.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)

        log_path = append_log_speech(
            log_base=log_base,
            transcript=transcript,
            confidence=confidence,
            is_final=is_final,
        )

    # Assert
    assert log_path is not None
    with open(log_path) as f:
        entry = json.loads(f.readline())

    assert entry["is_final"] is False
    assert entry["confidence"] == 0.7


def test_append_log_speech_coexists_with_window_logs(log_base: Path) -> None:
    """Test that speech logs can coexist with window logs in the same file.

    The function should:
    1. Append to the same hourly JSONL file as window logs
    2. Be distinguishable by the 'type' field
    3. Window logs should not have 'type' field (for backward compatibility)
    """
    from datetime import datetime
    from unittest.mock import patch

    from auto_daily.logger import append_log_hourly, append_log_speech

    # Arrange - fixed datetime for consistent file path
    fixed_dt = datetime(2025, 12, 27, 17, 30, 0)

    # Act - write window log first
    with patch("auto_daily.logger.datetime") as mock_dt:
        mock_dt.now.return_value = fixed_dt
        mock_dt.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)

        append_log_hourly(
            log_base=log_base,
            window_info={"app_name": "VSCode", "window_title": "test.py"},
            ocr_text="some code",
        )

    # Act - write speech log to the same file
    with patch("auto_daily.logger.datetime") as mock_dt:
        mock_dt.now.return_value = fixed_dt
        mock_dt.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)

        append_log_speech(
            log_base=log_base,
            transcript="音声テスト",
            confidence=0.9,
            is_final=True,
        )

    # Assert - both entries are in the same file
    log_path = log_base / "2025-12-27" / "activity_17.jsonl"
    assert log_path.exists()

    with open(log_path) as f:
        lines = f.readlines()

    assert len(lines) == 2

    window_entry = json.loads(lines[0])
    speech_entry = json.loads(lines[1])

    # Window entry has no 'type' field
    assert "type" not in window_entry
    assert "window_info" in window_entry

    # Speech entry has 'type' = 'speech'
    assert speech_entry["type"] == "speech"
    assert speech_entry["transcript"] == "音声テスト"
