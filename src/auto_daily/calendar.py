"""Calendar module for iCal integration (PBI-031, PBI-032)."""

from dataclasses import dataclass, field
from datetime import UTC, date, datetime, timedelta
from pathlib import Path

import httpx
import yaml
from icalendar import Calendar


@dataclass
class CalendarEvent:
    """Represents a calendar event."""

    summary: str
    start: datetime
    end: datetime
    calendar_name: str
    is_all_day: bool = False


@dataclass
class LogEntry:
    """Represents an activity log entry."""

    timestamp: datetime
    app_name: str
    window_title: str
    ocr_text: str = ""


@dataclass
class MatchResult:
    """Result of matching calendar events with activity logs.

    Attributes:
        matched: List of (event, logs) tuples where event has matching logs
        unstarted: Events that have no matching logs (scheduled but not worked on)
        unplanned: Logs that don't match any event (work done outside schedule)
    """

    matched: list[tuple[CalendarEvent, list[LogEntry]]] = field(default_factory=list)
    unstarted: list[CalendarEvent] = field(default_factory=list)
    unplanned: list[LogEntry] = field(default_factory=list)


def match_events_with_logs(
    events: list[CalendarEvent],
    logs: list[LogEntry],
    tolerance_minutes: int = 0,
) -> MatchResult:
    """Match calendar events with activity logs by time.

    Args:
        events: List of calendar events for the day
        logs: List of activity log entries
        tolerance_minutes: Extra minutes before/after event to consider as match

    Returns:
        MatchResult containing matched events, unstarted events, and unplanned logs
    """
    result = MatchResult()
    tolerance = timedelta(minutes=tolerance_minutes)

    # Track which logs have been matched
    matched_log_indices: set[int] = set()

    for event in events:
        event_start = event.start - tolerance
        event_end = event.end + tolerance

        matching_logs: list[LogEntry] = []
        for i, log in enumerate(logs):
            # Ensure log timestamp has timezone
            log_ts = log.timestamp
            if log_ts.tzinfo is None:
                log_ts = log_ts.replace(tzinfo=UTC)

            # Check if log falls within event time range
            if event_start <= log_ts <= event_end:
                matching_logs.append(log)
                matched_log_indices.add(i)

        if matching_logs:
            result.matched.append((event, matching_logs))
        else:
            result.unstarted.append(event)

    # Find unplanned logs (not matched to any event)
    for i, log in enumerate(logs):
        if i not in matched_log_indices:
            result.unplanned.append(log)

    return result


def load_calendar_config() -> list[dict]:
    """Load calendar configuration from YAML file.

    Priority order:
    1. Project root's calendar_config.yaml (current working directory)
    2. ~/.auto-daily/calendar_config.yaml

    Returns:
        List of calendar configurations, each with 'name' and 'ical_url'.
        Returns empty list if no config file exists.
    """
    # 1. Check project root
    project_config = Path.cwd() / "calendar_config.yaml"
    if project_config.exists():
        config = yaml.safe_load(project_config.read_text())
        return config.get("calendars", [])

    # 2. Check home directory
    home_config = Path.home() / ".auto-daily" / "calendar_config.yaml"
    if home_config.exists():
        config = yaml.safe_load(home_config.read_text())
        return config.get("calendars", [])

    return []


def _is_event_on_date(
    event_start: date | datetime, event_end: date | datetime, target_date: date
) -> bool:
    """Check if an event occurs on the target date.

    Args:
        event_start: Event start time/date
        event_end: Event end time/date
        target_date: The date to check

    Returns:
        True if the event overlaps with the target date
    """
    # Convert to date for comparison
    if isinstance(event_start, datetime):
        start_date = event_start.date()
    else:
        start_date = event_start

    if isinstance(event_end, datetime):
        end_date = event_end.date()
    else:
        # For all-day events, end date is exclusive
        end_date = event_end

    # Event overlaps if: start_date <= target_date < end_date
    # For all-day events with same start/end, use start_date == target_date
    if start_date == end_date:
        return start_date == target_date
    return start_date <= target_date < end_date


async def fetch_events(
    ical_url: str, target_date: date, calendar_name: str
) -> list[CalendarEvent]:
    """Fetch events from an iCal URL for a specific date.

    Args:
        ical_url: The iCal URL to fetch
        target_date: The date to filter events for
        calendar_name: Name of the calendar (for display)

    Returns:
        List of CalendarEvent objects for the target date
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(ical_url)
        response.raise_for_status()

    cal = Calendar.from_ical(response.content)
    events: list[CalendarEvent] = []

    for component in cal.walk():
        if component.name != "VEVENT":
            continue

        dtstart = component.get("dtstart")
        dtend = component.get("dtend")
        summary = str(component.get("summary", ""))

        if dtstart is None:
            continue

        start_value = dtstart.dt
        end_value = dtend.dt if dtend else start_value

        # Check if this is an all-day event (date vs datetime)
        is_all_day = isinstance(start_value, date) and not isinstance(
            start_value, datetime
        )

        # Check if event is on target date
        if not _is_event_on_date(start_value, end_value, target_date):
            continue

        # Convert to datetime for consistency
        if is_all_day:
            start_dt = datetime.combine(start_value, datetime.min.time(), tzinfo=UTC)
            end_dt = datetime.combine(end_value, datetime.min.time(), tzinfo=UTC)
        else:
            start_dt = (
                start_value if start_value.tzinfo else start_value.replace(tzinfo=UTC)
            )
            end_dt = end_value if end_value.tzinfo else end_value.replace(tzinfo=UTC)

        events.append(
            CalendarEvent(
                summary=summary,
                start=start_dt,
                end=end_dt,
                calendar_name=calendar_name,
                is_all_day=is_all_day,
            )
        )

    # Sort by start time
    events.sort(key=lambda e: e.start)
    return events


async def get_all_events(target_date: date) -> list[CalendarEvent]:
    """Get all events from all configured calendars.

    Args:
        target_date: The date to fetch events for

    Returns:
        List of CalendarEvent objects from all calendars, sorted by start time.
        Returns empty list if no calendars are configured.
    """
    calendars = load_calendar_config()
    if not calendars:
        return []

    all_events: list[CalendarEvent] = []

    for calendar in calendars:
        name = calendar.get("name", "Unknown")
        ical_url = calendar.get("ical_url")
        if not ical_url:
            continue

        try:
            events = await fetch_events(ical_url, target_date, name)
            all_events.extend(events)
        except (httpx.HTTPError, ValueError, KeyError):
            # Skip calendars that fail to fetch
            continue

    # Sort all events by start time
    all_events.sort(key=lambda e: e.start)
    return all_events
