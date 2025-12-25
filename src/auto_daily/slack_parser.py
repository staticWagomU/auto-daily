"""Slack window title parser module."""

import re
from typing import TypedDict


class SlackContext(TypedDict):
    """Slack context extracted from window title."""

    channel: str | None
    workspace: str | None
    dm_user: str | None
    is_thread: bool


def parse_slack_title(title: str) -> SlackContext:
    """Parse Slack window title to extract channel, workspace, and other context.

    Supports formats:
    - "#channel-name | Workspace Name"
    - "#channel-name - Workspace Name"
    - "@username | Workspace Name"
    - "Thread in #channel-name | Workspace Name"

    Args:
        title: The window title string from Slack.

    Returns:
        SlackContext with channel, workspace, dm_user, and is_thread fields.
    """
    result: SlackContext = {
        "channel": None,
        "workspace": None,
        "dm_user": None,
        "is_thread": False,
    }

    # Try to split by " | " or " - " to get workspace
    separator_match = re.search(r" [|\-] ", title)
    if not separator_match:
        return result

    separator_pos = separator_match.start()
    left_part = title[:separator_pos]
    workspace = title[separator_pos + 3 :].strip()
    result["workspace"] = workspace

    # Check for thread
    thread_match = re.match(r"Thread in #([\w-]+)", left_part)
    if thread_match:
        result["channel"] = thread_match.group(1)
        result["is_thread"] = True
        return result

    # Check for channel
    channel_match = re.match(r"#([\w-]+)", left_part)
    if channel_match:
        result["channel"] = channel_match.group(1)
        return result

    # Check for DM
    dm_match = re.match(r"@([\w.-]+)", left_part)
    if dm_match:
        result["dm_user"] = dm_match.group(1)
        return result

    return result
