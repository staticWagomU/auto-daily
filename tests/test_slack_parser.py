"""Tests for Slack window title parsing."""

from auto_daily.slack_parser import parse_slack_title


class TestChannelExtraction:
    """Tests for extracting channel name from Slack window title."""

    def test_channel_extraction_with_pipe_separator(self) -> None:
        """Test channel extraction with pipe separator."""
        title = "#general | My Workspace"
        result = parse_slack_title(title)
        assert result["channel"] == "general"

    def test_channel_extraction_with_dash_separator(self) -> None:
        """Test channel extraction with dash separator."""
        title = "#random - My Workspace"
        result = parse_slack_title(title)
        assert result["channel"] == "random"

    def test_channel_extraction_with_hyphenated_name(self) -> None:
        """Test channel extraction with hyphenated channel name."""
        title = "#dev-team-discussions | Company Slack"
        result = parse_slack_title(title)
        assert result["channel"] == "dev-team-discussions"

    def test_dm_extraction(self) -> None:
        """Test DM user extraction."""
        title = "@john.doe | My Workspace"
        result = parse_slack_title(title)
        assert result["channel"] is None
        assert result["dm_user"] == "john.doe"

    def test_thread_channel_extraction(self) -> None:
        """Test channel extraction from thread view."""
        title = "Thread in #general | My Workspace"
        result = parse_slack_title(title)
        assert result["channel"] == "general"
        assert result["is_thread"] is True

    def test_non_slack_title_returns_none(self) -> None:
        """Test that non-Slack titles return None values."""
        title = "Some Random Window Title"
        result = parse_slack_title(title)
        assert result["channel"] is None
        assert result["workspace"] is None


class TestWorkspaceExtraction:
    """Tests for extracting workspace name from Slack window title."""

    def test_workspace_extraction_with_pipe_separator(self) -> None:
        """Test workspace extraction with pipe separator."""
        title = "#general | My Workspace"
        result = parse_slack_title(title)
        assert result["workspace"] == "My Workspace"

    def test_workspace_extraction_with_dash_separator(self) -> None:
        """Test workspace extraction with dash separator."""
        title = "#random - Company Slack"
        result = parse_slack_title(title)
        assert result["workspace"] == "Company Slack"

    def test_workspace_with_multiple_words(self) -> None:
        """Test workspace extraction with multiple words."""
        title = "#dev | Acme Corporation Workspace"
        result = parse_slack_title(title)
        assert result["workspace"] == "Acme Corporation Workspace"

    def test_workspace_from_dm(self) -> None:
        """Test workspace extraction from DM title."""
        title = "@alice | Team Slack"
        result = parse_slack_title(title)
        assert result["workspace"] == "Team Slack"

    def test_workspace_from_thread(self) -> None:
        """Test workspace extraction from thread title."""
        title = "Thread in #general | My Workspace"
        result = parse_slack_title(title)
        assert result["workspace"] == "My Workspace"


class TestSlackContextInLog:
    """Tests for Slack context integration with logging."""

    def test_slack_context_structure(self) -> None:
        """Test that parse_slack_title returns proper context structure."""
        title = "#general | My Workspace"
        result = parse_slack_title(title)

        assert "channel" in result
        assert "workspace" in result
        assert "dm_user" in result
        assert "is_thread" in result

    def test_slack_context_for_channel(self) -> None:
        """Test Slack context for a regular channel."""
        title = "#dev-team | Company"
        result = parse_slack_title(title)

        assert result["channel"] == "dev-team"
        assert result["workspace"] == "Company"
        assert result["dm_user"] is None
        assert result["is_thread"] is False

    def test_slack_context_for_dm(self) -> None:
        """Test Slack context for a DM."""
        title = "@bob | Company"
        result = parse_slack_title(title)

        assert result["channel"] is None
        assert result["workspace"] == "Company"
        assert result["dm_user"] == "bob"
        assert result["is_thread"] is False

    def test_slack_context_for_thread(self) -> None:
        """Test Slack context for a thread."""
        title = "Thread in #random | Company"
        result = parse_slack_title(title)

        assert result["channel"] == "random"
        assert result["workspace"] == "Company"
        assert result["dm_user"] is None
        assert result["is_thread"] is True


class TestConversationExtraction:
    """Tests for extracting conversation messages from OCR text."""

    def test_conversation_extraction(self) -> None:
        """Test extracting messages from OCR text.

        The function should:
        1. Parse OCR text and identify message patterns
        2. Extract username, timestamp, and content for each message
        3. Return a list of Message TypedDicts
        """
        from auto_daily.slack_parser import extract_conversations

        ocr_text = """taro.yamada  10:30
おはようございます！今日のミーティングは14時からです。

hanako.suzuki  10:32
了解です！議題は何ですか？

taro.yamada  10:35
新機能の進捗確認と、来週のリリース計画についてです。
"""

        messages = extract_conversations(ocr_text)

        assert len(messages) == 3

        assert messages[0]["username"] == "taro.yamada"
        assert messages[0]["timestamp"] == "10:30"
        assert "おはようございます" in messages[0]["content"]

        assert messages[1]["username"] == "hanako.suzuki"
        assert messages[1]["timestamp"] == "10:32"
        assert "了解です" in messages[1]["content"]

        assert messages[2]["username"] == "taro.yamada"
        assert messages[2]["timestamp"] == "10:35"
        assert "新機能の進捗確認" in messages[2]["content"]

    def test_conversation_extraction_with_am_pm(self) -> None:
        """Test extracting messages with AM/PM time format."""
        from auto_daily.slack_parser import extract_conversations

        ocr_text = """alice  2:30 PM
Hey, are you available for a quick call?

bob  2:35 PM
Sure, let me wrap up what I'm doing.
"""

        messages = extract_conversations(ocr_text)

        assert len(messages) == 2
        assert messages[0]["username"] == "alice"
        assert messages[0]["timestamp"] == "2:30 PM"
        assert messages[1]["username"] == "bob"
        assert messages[1]["timestamp"] == "2:35 PM"

    def test_conversation_extraction_empty_text(self) -> None:
        """Test extracting from empty or no-message text."""
        from auto_daily.slack_parser import extract_conversations

        messages = extract_conversations("")
        assert messages == []

        messages = extract_conversations(
            "This is just some random text without messages."
        )
        assert messages == []


class TestMyMessageFilter:
    """Tests for filtering messages by username."""

    def test_my_message_filter(self) -> None:
        """Test filtering messages by a specific username.

        The function should:
        1. Take a list of messages and a username
        2. Return only messages from that username
        3. Preserve message order
        """
        from auto_daily.slack_parser import Message, filter_my_messages

        messages: list[Message] = [
            {"username": "taro.yamada", "timestamp": "10:30", "content": "おはよう"},
            {
                "username": "hanako.suzuki",
                "timestamp": "10:32",
                "content": "おはよう！",
            },
            {"username": "taro.yamada", "timestamp": "10:35", "content": "今日の予定"},
            {"username": "jiro.tanaka", "timestamp": "10:40", "content": "了解"},
        ]

        my_messages = filter_my_messages(messages, "taro.yamada")

        assert len(my_messages) == 2
        assert my_messages[0]["content"] == "おはよう"
        assert my_messages[1]["content"] == "今日の予定"

    def test_my_message_filter_no_matches(self) -> None:
        """Test filter when no messages match the username."""
        from auto_daily.slack_parser import Message, filter_my_messages

        messages: list[Message] = [
            {"username": "alice", "timestamp": "10:30", "content": "Hello"},
            {"username": "bob", "timestamp": "10:32", "content": "Hi!"},
        ]

        my_messages = filter_my_messages(messages, "charlie")
        assert my_messages == []

    def test_my_message_filter_empty_list(self) -> None:
        """Test filter with empty message list."""
        from auto_daily.slack_parser import filter_my_messages

        my_messages = filter_my_messages([], "anyone")
        assert my_messages == []
