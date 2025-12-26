"""OCR text noise filtering.

This module provides filters to clean up OCR output by removing
noise such as menu bar elements, sensitive strings, and garbage characters.
"""

import re
from collections.abc import Callable


class OCRFilter:
    """OCR text noise filter.

    Applies multiple filters to clean up OCR output:
    - Menu bar elements (time, battery, day abbreviations)
    - Sensitive strings (API keys, tokens)
    - Garbage characters (symbol sequences)
    - Repeated lines
    """

    def __init__(self) -> None:
        """Initialize the OCR filter with default filters."""
        self.filters: list[Callable[[str], str]] = [
            self._filter_menu_bar,
            self._filter_sensitive_strings,
            self._filter_garbage_chars,
            self._filter_repeated_lines,
        ]

    def filter(self, text: str) -> str:
        """Apply all filters to the text.

        Args:
            text: Raw OCR text to filter.

        Returns:
            Filtered text with noise removed.
        """
        for f in self.filters:
            text = f(text)
        return text.strip()

    def _filter_menu_bar(self, text: str) -> str:
        """Remove menu bar elements like time, battery, and day abbreviations.

        Args:
            text: Text to filter.

        Returns:
            Text with menu bar elements removed.
        """
        patterns = [
            r"^\s*\d{1,2}:\d{2}\s*(AM|PM)?\s*$",  # Time (12:30, 12:30 AM)
            r"^\s*\d{1,3}%\s*$",  # Battery percentage
            r"^\s*(Mon|Tue|Wed|Thu|Fri|Sat|Sun)\s*$",  # Day abbreviations
        ]
        lines = text.split("\n")
        filtered_lines = [
            line
            for line in lines
            if not any(re.match(p, line, re.IGNORECASE) for p in patterns)
        ]
        return "\n".join(filtered_lines)

    def _filter_sensitive_strings(self, text: str) -> str:
        """Replace sensitive strings with [REDACTED].

        Detects:
        - Long alphanumeric strings (32+ characters) that look like API keys
        - Bearer tokens

        Args:
            text: Text to filter.

        Returns:
            Text with sensitive strings redacted.
        """
        # Long alphanumeric strings (API keys, tokens, etc.)
        text = re.sub(r"\b[A-Za-z0-9_]{32,}\b", "[REDACTED]", text)

        # Bearer tokens
        text = re.sub(r"Bearer\s+[A-Za-z0-9._-]+", "Bearer [REDACTED]", text)

        return text

    def _filter_garbage_chars(self, text: str) -> str:
        """Remove sequences of 3+ consecutive symbols.

        Args:
            text: Text to filter.

        Returns:
            Text with garbage character sequences removed.
        """
        # Remove lines that are only symbols (3+ consecutive)
        lines = text.split("\n")
        filtered_lines = []
        for line in lines:
            # Check if line is mostly garbage symbols
            cleaned = re.sub(r"[^\w\s]{3,}", "", line)
            if cleaned.strip() or not line.strip():
                filtered_lines.append(cleaned)
        return "\n".join(filtered_lines)

    def _filter_repeated_lines(self, text: str) -> str:
        """Remove duplicate lines, keeping the first occurrence.

        Empty lines are preserved.

        Args:
            text: Text to filter.

        Returns:
            Text with duplicate lines removed.
        """
        lines = text.split("\n")
        seen: set[str] = set()
        result: list[str] = []

        for line in lines:
            stripped = line.strip()
            if stripped:
                if stripped not in seen:
                    seen.add(stripped)
                    result.append(line)
            else:
                result.append(line)

        return "\n".join(result)
