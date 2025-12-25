"""Tests for calendar module (PBI-031, PBI-032)."""

import os
from datetime import UTC, date, datetime
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest


class TestLoadCalendarConfig:
    """Tests for loading calendar configuration."""

    def test_load_calendar_config(self, tmp_path: Path) -> None:
        """Test that calendar_config.yaml is loaded from project root.

        The config should:
        1. Read calendar_config.yaml from the current working directory
        2. Parse YAML structure with calendars list
        3. Return list of calendar dictionaries with name and ical_url
        """
        from auto_daily.calendar import load_calendar_config

        # Arrange: Create calendar_config.yaml in tmp_path
        config_file = tmp_path / "calendar_config.yaml"
        config_content = """calendars:
  - name: "仕事"
    ical_url: "https://calendar.google.com/calendar/ical/work/basic.ics"
  - name: "個人"
    ical_url: "https://calendar.google.com/calendar/ical/personal/basic.ics"
"""
        config_file.write_text(config_content)

        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)

            # Act: Load calendar config
            result = load_calendar_config()

            # Assert: Should return list of calendar configs
            assert len(result) == 2
            assert result[0]["name"] == "仕事"
            assert (
                result[0]["ical_url"]
                == "https://calendar.google.com/calendar/ical/work/basic.ics"
            )
            assert result[1]["name"] == "個人"
            assert (
                result[1]["ical_url"]
                == "https://calendar.google.com/calendar/ical/personal/basic.ics"
            )
        finally:
            os.chdir(original_cwd)

    def test_load_calendar_config_fallback_to_home(self, tmp_path: Path) -> None:
        """Test that calendar_config.yaml falls back to home directory.

        When not in project root, should check ~/.auto-daily/calendar_config.yaml
        """
        from auto_daily.calendar import load_calendar_config

        # Arrange: Create empty project root (no calendar_config.yaml)
        project_root = tmp_path / "project"
        project_root.mkdir()

        # Create calendar_config.yaml in simulated home directory
        home_dir = tmp_path / "home"
        config_dir = home_dir / ".auto-daily"
        config_dir.mkdir(parents=True)
        config_file = config_dir / "calendar_config.yaml"
        config_content = """calendars:
  - name: "Home Calendar"
    ical_url: "https://calendar.google.com/calendar/ical/home/basic.ics"
"""
        config_file.write_text(config_content)

        original_cwd = os.getcwd()
        try:
            os.chdir(project_root)

            with patch("auto_daily.calendar.Path.home", return_value=home_dir):
                # Act: Load calendar config
                result = load_calendar_config()

                # Assert: Should return home directory config
                assert len(result) == 1
                assert result[0]["name"] == "Home Calendar"
        finally:
            os.chdir(original_cwd)

    def test_no_calendar_config(self, tmp_path: Path) -> None:
        """Test that empty list is returned when no config file exists.

        When calendar_config.yaml is not found in either location:
        1. Should not raise an error
        2. Should return an empty list
        """
        from auto_daily.calendar import load_calendar_config

        # Arrange: Create empty project root (no calendar_config.yaml)
        project_root = tmp_path / "project"
        project_root.mkdir()

        # Create home directory without calendar_config.yaml
        home_dir = tmp_path / "home"
        config_dir = home_dir / ".auto-daily"
        config_dir.mkdir(parents=True)

        original_cwd = os.getcwd()
        try:
            os.chdir(project_root)

            with patch("auto_daily.calendar.Path.home", return_value=home_dir):
                # Act: Load calendar config when neither file exists
                result = load_calendar_config()

                # Assert: Should return empty list
                assert result == []
        finally:
            os.chdir(original_cwd)


class TestFetchEventsFromIcal:
    """Tests for fetching events from iCal URL."""

    @pytest.mark.asyncio
    async def test_fetch_events_from_ical(self) -> None:
        """Test that events can be fetched from an iCal URL.

        The function should:
        1. Fetch iCal data from the URL
        2. Parse the iCal format
        3. Filter events for the target date
        4. Return list of CalendarEvent objects
        """
        from auto_daily.calendar import CalendarEvent, fetch_events

        # Arrange: Create mock iCal data
        ical_data = b"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Test//Test//EN
BEGIN:VEVENT
DTSTART:20251225T100000Z
DTEND:20251225T110000Z
SUMMARY:Christmas Meeting
UID:test-event-1@test.com
END:VEVENT
BEGIN:VEVENT
DTSTART:20251225T140000Z
DTEND:20251225T150000Z
SUMMARY:Christmas Lunch
UID:test-event-2@test.com
END:VEVENT
BEGIN:VEVENT
DTSTART:20251226T100000Z
DTEND:20251226T110000Z
SUMMARY:Day After Christmas
UID:test-event-3@test.com
END:VEVENT
END:VCALENDAR"""

        # Mock httpx response
        mock_response = AsyncMock()
        mock_response.content = ical_data
        mock_response.raise_for_status = lambda: None

        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                return_value=mock_response
            )

            # Act: Fetch events for 2025-12-25
            target_date = date(2025, 12, 25)
            events = await fetch_events(
                "https://example.com/calendar.ics", target_date, "Test Calendar"
            )

            # Assert: Should return 2 events for Christmas day
            assert len(events) == 2
            assert all(isinstance(e, CalendarEvent) for e in events)
            assert events[0].summary == "Christmas Meeting"
            assert events[1].summary == "Christmas Lunch"
            assert all(e.calendar_name == "Test Calendar" for e in events)

    @pytest.mark.asyncio
    async def test_fetch_events_with_all_day_event(self) -> None:
        """Test that all-day events are correctly handled.

        All-day events use DATE instead of DATETIME.
        """
        from auto_daily.calendar import fetch_events

        # Arrange: Create mock iCal data with all-day event
        ical_data = b"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Test//Test//EN
BEGIN:VEVENT
DTSTART;VALUE=DATE:20251225
DTEND;VALUE=DATE:20251226
SUMMARY:Christmas Holiday
UID:test-allday@test.com
END:VEVENT
END:VCALENDAR"""

        mock_response = AsyncMock()
        mock_response.content = ical_data
        mock_response.raise_for_status = lambda: None

        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                return_value=mock_response
            )

            # Act: Fetch events for 2025-12-25
            target_date = date(2025, 12, 25)
            events = await fetch_events(
                "https://example.com/calendar.ics", target_date, "Test"
            )

            # Assert: Should include the all-day event
            assert len(events) == 1
            assert events[0].summary == "Christmas Holiday"
            assert events[0].is_all_day is True


class TestMergeMultipleCalendars:
    """Tests for merging events from multiple calendars."""

    @pytest.mark.asyncio
    async def test_merge_multiple_calendars(self, tmp_path: Path) -> None:
        """Test that events from multiple calendars are merged.

        The function should:
        1. Load all calendar configs
        2. Fetch events from each calendar
        3. Merge and sort events by start time
        4. Return combined list of CalendarEvent objects
        """
        from auto_daily.calendar import get_all_events

        # Arrange: Create calendar config with 2 calendars
        config_file = tmp_path / "calendar_config.yaml"
        config_content = """calendars:
  - name: "Work"
    ical_url: "https://example.com/work.ics"
  - name: "Personal"
    ical_url: "https://example.com/personal.ics"
"""
        config_file.write_text(config_content)

        # Mock iCal responses
        work_ical = b"""BEGIN:VCALENDAR
VERSION:2.0
BEGIN:VEVENT
DTSTART:20251225T090000Z
DTEND:20251225T100000Z
SUMMARY:Work Meeting
UID:work-1@test.com
END:VEVENT
END:VCALENDAR"""

        personal_ical = b"""BEGIN:VCALENDAR
VERSION:2.0
BEGIN:VEVENT
DTSTART:20251225T120000Z
DTEND:20251225T130000Z
SUMMARY:Personal Lunch
UID:personal-1@test.com
END:VEVENT
END:VCALENDAR"""

        async def mock_get(url: str, *args, **kwargs) -> AsyncMock:
            response = AsyncMock()
            if "work" in url:
                response.content = work_ical
            else:
                response.content = personal_ical
            response.raise_for_status = lambda: None
            return response

        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)

            with patch("httpx.AsyncClient") as mock_client:
                mock_client.return_value.__aenter__.return_value.get = mock_get

                # Act: Get all events for 2025-12-25
                target_date = date(2025, 12, 25)
                events = await get_all_events(target_date)

                # Assert: Should have 2 events, sorted by start time
                assert len(events) == 2
                assert events[0].summary == "Work Meeting"
                assert events[0].calendar_name == "Work"
                assert events[1].summary == "Personal Lunch"
                assert events[1].calendar_name == "Personal"
        finally:
            os.chdir(original_cwd)

    @pytest.mark.asyncio
    async def test_get_all_events_no_config(self, tmp_path: Path) -> None:
        """Test that empty list is returned when no calendar is configured."""
        from auto_daily.calendar import get_all_events

        # Arrange: Create empty project root
        project_root = tmp_path / "project"
        project_root.mkdir()

        home_dir = tmp_path / "home"
        config_dir = home_dir / ".auto-daily"
        config_dir.mkdir(parents=True)

        original_cwd = os.getcwd()
        try:
            os.chdir(project_root)

            with patch("auto_daily.calendar.Path.home", return_value=home_dir):
                # Act: Get all events when no config exists
                target_date = date(2025, 12, 25)
                events = await get_all_events(target_date)

                # Assert: Should return empty list
                assert events == []
        finally:
            os.chdir(original_cwd)


class TestMatchEventsWithLogs:
    """Tests for matching calendar events with activity logs (PBI-032)."""

    def test_match_events_with_logs(self) -> None:
        """Test that events and logs are matched by time.

        The function should:
        1. Compare event time ranges with log timestamps
        2. Match logs that fall within event time ± tolerance
        3. Return MatchResult with matched, unstarted, and unplanned lists
        """
        from auto_daily.calendar import (
            CalendarEvent,
            LogEntry,
            MatchResult,
            match_events_with_logs,
        )

        # Arrange: Create events and logs
        events = [
            CalendarEvent(
                summary="Morning Meeting",
                start=datetime(2025, 12, 25, 9, 0, tzinfo=UTC),
                end=datetime(2025, 12, 25, 10, 0, tzinfo=UTC),
                calendar_name="Work",
            ),
            CalendarEvent(
                summary="Lunch Break",
                start=datetime(2025, 12, 25, 12, 0, tzinfo=UTC),
                end=datetime(2025, 12, 25, 13, 0, tzinfo=UTC),
                calendar_name="Personal",
            ),
        ]

        logs = [
            LogEntry(
                timestamp=datetime(2025, 12, 25, 9, 15, tzinfo=UTC),
                app_name="Zoom",
                window_title="Morning Meeting",
            ),
            LogEntry(
                timestamp=datetime(2025, 12, 25, 9, 45, tzinfo=UTC),
                app_name="Zoom",
                window_title="Morning Meeting",
            ),
            LogEntry(
                timestamp=datetime(2025, 12, 25, 12, 30, tzinfo=UTC),
                app_name="Safari",
                window_title="News",
            ),
        ]

        # Act: Match events with logs
        result = match_events_with_logs(events, logs)

        # Assert: Should return MatchResult
        assert isinstance(result, MatchResult)
        assert len(result.matched) == 2  # Both events have matching logs
        # First event matched with 2 logs
        assert result.matched[0][0].summary == "Morning Meeting"
        assert len(result.matched[0][1]) == 2
        # Second event matched with 1 log
        assert result.matched[1][0].summary == "Lunch Break"
        assert len(result.matched[1][1]) == 1

    def test_detect_unstarted_events(self) -> None:
        """Test that events without logs are marked as unstarted.

        When an event has no matching logs within its time range,
        it should be added to the unstarted list.
        """
        from auto_daily.calendar import (
            CalendarEvent,
            LogEntry,
            match_events_with_logs,
        )

        # Arrange: Event with no matching logs
        events = [
            CalendarEvent(
                summary="Skipped Meeting",
                start=datetime(2025, 12, 25, 14, 0, tzinfo=UTC),
                end=datetime(2025, 12, 25, 15, 0, tzinfo=UTC),
                calendar_name="Work",
            ),
        ]

        logs = [
            LogEntry(
                timestamp=datetime(2025, 12, 25, 9, 0, tzinfo=UTC),
                app_name="Code",
                window_title="main.py",
            ),
        ]

        # Act: Match events with logs
        result = match_events_with_logs(events, logs)

        # Assert: Event should be in unstarted list
        assert len(result.unstarted) == 1
        assert result.unstarted[0].summary == "Skipped Meeting"
        assert len(result.matched) == 0

    def test_detect_unplanned_work(self) -> None:
        """Test that logs without matching events are marked as unplanned.

        When a log doesn't fall within any event's time range,
        it should be added to the unplanned list.
        """
        from auto_daily.calendar import (
            CalendarEvent,
            LogEntry,
            match_events_with_logs,
        )

        # Arrange: Log with no matching event
        events = [
            CalendarEvent(
                summary="Morning Meeting",
                start=datetime(2025, 12, 25, 9, 0, tzinfo=UTC),
                end=datetime(2025, 12, 25, 10, 0, tzinfo=UTC),
                calendar_name="Work",
            ),
        ]

        logs = [
            LogEntry(
                timestamp=datetime(2025, 12, 25, 11, 0, tzinfo=UTC),
                app_name="Code",
                window_title="Bug fix",
            ),
            LogEntry(
                timestamp=datetime(2025, 12, 25, 16, 0, tzinfo=UTC),
                app_name="Slack",
                window_title="Urgent issue",
            ),
        ]

        # Act: Match events with logs
        result = match_events_with_logs(events, logs)

        # Assert: Logs should be in unplanned list
        assert len(result.unplanned) == 2
        assert result.unplanned[0].app_name == "Code"
        assert result.unplanned[1].app_name == "Slack"


class TestCalendarInReportPrompt:
    """Tests for calendar information in report prompt (PBI-032)."""

    def test_calendar_in_report_prompt(self, tmp_path: Path) -> None:
        """Test that calendar info and match results are included in prompt.

        The prompt should contain:
        1. List of today's events
        2. Matched events with logs
        3. Unstarted events
        4. Unplanned work
        """
        from auto_daily.calendar import CalendarEvent, LogEntry, MatchResult
        from auto_daily.ollama import generate_daily_report_prompt_with_calendar

        # Arrange: Create log file and match result
        log_file = tmp_path / "activity_2025-12-25.jsonl"
        log_file.write_text(
            '{"timestamp": "2025-12-25T09:15:00", "window_info": {"app_name": "Zoom"}, "ocr_text": "Meeting"}\n'
        )

        match_result = MatchResult(
            matched=[
                (
                    CalendarEvent(
                        summary="Morning Meeting",
                        start=datetime(2025, 12, 25, 9, 0, tzinfo=UTC),
                        end=datetime(2025, 12, 25, 10, 0, tzinfo=UTC),
                        calendar_name="Work",
                    ),
                    [
                        LogEntry(
                            timestamp=datetime(2025, 12, 25, 9, 15, tzinfo=UTC),
                            app_name="Zoom",
                            window_title="Meeting",
                        )
                    ],
                )
            ],
            unstarted=[
                CalendarEvent(
                    summary="1on1",
                    start=datetime(2025, 12, 25, 16, 0, tzinfo=UTC),
                    end=datetime(2025, 12, 25, 17, 0, tzinfo=UTC),
                    calendar_name="Work",
                )
            ],
            unplanned=[
                LogEntry(
                    timestamp=datetime(2025, 12, 25, 11, 0, tzinfo=UTC),
                    app_name="Code",
                    window_title="Bug fix",
                )
            ],
        )

        # Act: Generate prompt with calendar
        prompt = generate_daily_report_prompt_with_calendar(log_file, match_result)

        # Assert: Prompt should contain calendar sections
        assert "今日の予定" in prompt or "Today's Schedule" in prompt
        assert "Morning Meeting" in prompt
        assert "予定通り実施" in prompt or "Completed as Planned" in prompt
        assert "未着手" in prompt or "Unstarted" in prompt
        assert "1on1" in prompt
        assert "予定外" in prompt or "Unplanned" in prompt
        assert "Bug fix" in prompt
