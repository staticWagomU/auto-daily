"""Tests for calendar module (PBI-031)."""

import os
from datetime import date
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
