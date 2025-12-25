"""Slack window title parser module."""

import re
from typing import TypedDict


class SlackContext(TypedDict):
    """Slack context extracted from window title."""

    channel: str | None
    workspace: str | None
    dm_user: str | None
    is_thread: bool


class Message(TypedDict):
    """A single message extracted from Slack conversation."""

    username: str
    timestamp: str
    content: str


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


def extract_conversations(ocr_text: str) -> list[Message]:
    """Extract conversation messages from OCR text.

    Parses OCR text looking for message patterns like:
    - "username  HH:MM" (24-hour format)
    - "username  H:MM AM/PM" (12-hour format)

    Args:
        ocr_text: The OCR-extracted text from a Slack window.

    Returns:
        List of Message TypedDicts with username, timestamp, and content.
    """
    if not ocr_text.strip():
        return []

    messages: list[Message] = []

    # Pattern: username (with dots, underscores, hyphens) followed by 2+ spaces and time
    # Time can be HH:MM or H:MM with optional AM/PM
    pattern = r"^([\w.-]+)\s{2,}(\d{1,2}:\d{2}(?:\s*[AP]M)?)\s*$"

    lines = ocr_text.split("\n")
    current_message: Message | None = None

    for line in lines:
        match = re.match(pattern, line.strip())
        if match:
            # Save previous message if exists
            if current_message is not None:
                messages.append(current_message)

            # Start new message
            current_message = {
                "username": match.group(1),
                "timestamp": match.group(2),
                "content": "",
            }
        elif current_message is not None and line.strip():
            # Append content to current message
            if current_message["content"]:
                current_message["content"] += "\n" + line.strip()
            else:
                current_message["content"] = line.strip()

    # Don't forget the last message
    if current_message is not None:
        messages.append(current_message)

    return messages
