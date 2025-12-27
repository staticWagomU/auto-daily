"""Tests for speech recognition module (PBI-046c).

This module tests the SpeechRecognizer class which provides real-time
speech-to-text functionality using Apple's Speech Framework.
"""

from collections.abc import Callable
from unittest.mock import MagicMock, patch

# ============================================================
# ST-001: SpeechRecognizer basic structure tests
# ============================================================


def test_speech_recognizer_init() -> None:
    """Test that SpeechRecognizer can be instantiated with a callback.

    The class should:
    1. Accept an on_result callback function
    2. Accept an optional language parameter (default: ja-JP)
    3. Store the callback for later use
    """
    from auto_daily.speech import SpeechRecognizer

    # Arrange: Create a mock callback
    mock_callback: Callable[[str, float, bool], None] = MagicMock()

    # Act: Create a SpeechRecognizer instance
    recognizer = SpeechRecognizer(on_result=mock_callback)

    # Assert: Instance should be created successfully
    assert recognizer is not None
    assert recognizer._on_result == mock_callback
    assert recognizer._language == "ja-JP"


def test_speech_recognizer_init_with_custom_language() -> None:
    """Test that SpeechRecognizer can be instantiated with a custom language.

    The class should accept different language codes like "en-US".
    """
    from auto_daily.speech import SpeechRecognizer

    # Arrange: Create a mock callback
    mock_callback: Callable[[str, float, bool], None] = MagicMock()

    # Act: Create a SpeechRecognizer with English
    recognizer = SpeechRecognizer(on_result=mock_callback, language="en-US")

    # Assert: Language should be set correctly
    assert recognizer._language == "en-US"


def test_speech_recognizer_is_running_initially_false() -> None:
    """Test that is_running() returns False initially.

    Before start() is called, the recognizer should not be running.
    """
    from auto_daily.speech import SpeechRecognizer

    # Arrange: Create a SpeechRecognizer instance
    mock_callback: Callable[[str, float, bool], None] = MagicMock()
    recognizer = SpeechRecognizer(on_result=mock_callback)

    # Act & Assert: is_running should be False initially
    assert recognizer.is_running() is False


def test_speech_recognizer_start_sets_running() -> None:
    """Test that start() sets is_running to True.

    After calling start(), the recognizer should report running status.
    """
    from auto_daily.speech import SpeechRecognizer

    # Arrange: Create a SpeechRecognizer instance with mocked macOS APIs
    mock_callback: Callable[[str, float, bool], None] = MagicMock()

    with (
        patch("auto_daily.speech.SFSpeechRecognizer") as mock_sf_recognizer,
        patch("auto_daily.speech.AVAudioEngine") as mock_audio_engine,
        patch(
            "auto_daily.speech.SFSpeechAudioBufferRecognitionRequest"
        ) as mock_request,
    ):
        # Setup mocks
        mock_sf_recognizer_instance = MagicMock()
        mock_sf_recognizer.alloc.return_value.initWithLocale_.return_value = (
            mock_sf_recognizer_instance
        )
        mock_sf_recognizer_instance.isAvailable.return_value = True

        mock_audio_engine_instance = MagicMock()
        mock_audio_engine.alloc.return_value.init.return_value = (
            mock_audio_engine_instance
        )

        mock_input_node = MagicMock()
        mock_audio_engine_instance.inputNode.return_value = mock_input_node

        mock_audio_format = MagicMock()
        mock_input_node.outputFormatForBus_.return_value = mock_audio_format

        mock_request_instance = MagicMock()
        mock_request.alloc.return_value.init.return_value = mock_request_instance

        recognizer = SpeechRecognizer(on_result=mock_callback)

        # Act: Start the recognizer
        recognizer.start()

        # Assert: is_running should be True
        assert recognizer.is_running() is True


def test_speech_recognizer_stop_clears_running() -> None:
    """Test that stop() sets is_running back to False.

    After calling stop(), the recognizer should not be running.
    """
    from auto_daily.speech import SpeechRecognizer

    # Arrange: Create a SpeechRecognizer instance with mocked macOS APIs
    mock_callback: Callable[[str, float, bool], None] = MagicMock()

    with (
        patch("auto_daily.speech.SFSpeechRecognizer") as mock_sf_recognizer,
        patch("auto_daily.speech.AVAudioEngine") as mock_audio_engine,
        patch(
            "auto_daily.speech.SFSpeechAudioBufferRecognitionRequest"
        ) as mock_request,
    ):
        # Setup mocks
        mock_sf_recognizer_instance = MagicMock()
        mock_sf_recognizer.alloc.return_value.initWithLocale_.return_value = (
            mock_sf_recognizer_instance
        )
        mock_sf_recognizer_instance.isAvailable.return_value = True

        mock_audio_engine_instance = MagicMock()
        mock_audio_engine.alloc.return_value.init.return_value = (
            mock_audio_engine_instance
        )

        mock_input_node = MagicMock()
        mock_audio_engine_instance.inputNode.return_value = mock_input_node

        mock_audio_format = MagicMock()
        mock_input_node.outputFormatForBus_.return_value = mock_audio_format

        mock_request_instance = MagicMock()
        mock_request.alloc.return_value.init.return_value = mock_request_instance

        recognizer = SpeechRecognizer(on_result=mock_callback)
        recognizer.start()

        # Act: Stop the recognizer
        recognizer.stop()

        # Assert: is_running should be False
        assert recognizer.is_running() is False


def test_speech_recognizer_stop_without_start() -> None:
    """Test that stop() is safe to call even if not started.

    Calling stop() when not running should not raise an error.
    """
    from auto_daily.speech import SpeechRecognizer

    # Arrange: Create a SpeechRecognizer instance (not started)
    mock_callback: Callable[[str, float, bool], None] = MagicMock()
    recognizer = SpeechRecognizer(on_result=mock_callback)

    # Act & Assert: stop() should not raise
    recognizer.stop()
    assert recognizer.is_running() is False


# ============================================================
# ST-002: Callback invocation tests
# ============================================================


def test_speech_recognizer_callback_on_result() -> None:
    """Test that the callback is invoked when speech is recognized.

    The callback should receive:
    1. transcript: The recognized text
    2. confidence: A confidence score (0.0-1.0)
    3. is_final: Whether this is a final result
    """
    from auto_daily.speech import SpeechRecognizer

    # Arrange: Create a SpeechRecognizer with a tracking callback
    results: list[tuple[str, float, bool]] = []

    def track_callback(transcript: str, confidence: float, is_final: bool) -> None:
        results.append((transcript, confidence, is_final))

    recognizer = SpeechRecognizer(on_result=track_callback)

    # Act: Simulate a recognition result by calling internal method
    recognizer._handle_result("テスト", 0.9, False)

    # Assert: Callback should have been called
    assert len(results) == 1
    assert results[0] == ("テスト", 0.9, False)


def test_speech_recognizer_callback_with_final_result() -> None:
    """Test that is_final=True is passed for final results.

    Final results indicate the user has finished speaking a phrase.
    """
    from auto_daily.speech import SpeechRecognizer

    # Arrange: Create a SpeechRecognizer with a tracking callback
    results: list[tuple[str, float, bool]] = []

    def track_callback(transcript: str, confidence: float, is_final: bool) -> None:
        results.append((transcript, confidence, is_final))

    recognizer = SpeechRecognizer(on_result=track_callback)

    # Act: Simulate interim and final results
    recognizer._handle_result("テス", 0.7, False)  # Interim
    recognizer._handle_result("テスト", 0.95, True)  # Final

    # Assert: Both results should be captured with correct is_final values
    assert len(results) == 2
    assert results[0][2] is False  # Interim
    assert results[1][2] is True  # Final


def test_speech_recognizer_callback_confidence_range() -> None:
    """Test that confidence values are in valid range (0.0-1.0).

    The confidence value should always be between 0 and 1.
    """
    from auto_daily.speech import SpeechRecognizer

    # Arrange: Create a SpeechRecognizer with a tracking callback
    results: list[tuple[str, float, bool]] = []

    def track_callback(transcript: str, confidence: float, is_final: bool) -> None:
        results.append((transcript, confidence, is_final))

    recognizer = SpeechRecognizer(on_result=track_callback)

    # Act: Simulate results with various confidence values
    recognizer._handle_result("low", 0.1, True)
    recognizer._handle_result("medium", 0.5, True)
    recognizer._handle_result("high", 0.99, True)

    # Assert: All confidence values should be in valid range
    for _, confidence, _ in results:
        assert 0.0 <= confidence <= 1.0


def test_speech_recognizer_thread_safety() -> None:
    """Test that is_running is thread-safe using Lock.

    The SpeechRecognizer should use threading.Lock to protect state.
    """
    from auto_daily.speech import SpeechRecognizer

    # Arrange: Create a SpeechRecognizer instance
    mock_callback: Callable[[str, float, bool], None] = MagicMock()
    recognizer = SpeechRecognizer(on_result=mock_callback)

    # Assert: Internal lock should exist
    assert hasattr(recognizer, "_lock")
    # Lock should have acquire and release methods (duck typing for Lock/RLock)
    assert hasattr(recognizer._lock, "acquire")
    assert hasattr(recognizer._lock, "release")
    # Verify it's a threading lock type by checking _thread module
    lock_type = type(recognizer._lock)
    assert "_thread" in lock_type.__module__ or "threading" in lock_type.__module__


def test_speech_recognizer_language_accessor() -> None:
    """Test that the language can be accessed.

    The recognizer should provide access to the configured language.
    """
    from auto_daily.speech import SpeechRecognizer

    # Arrange & Act
    mock_callback: Callable[[str, float, bool], None] = MagicMock()
    recognizer = SpeechRecognizer(on_result=mock_callback, language="en-US")

    # Assert
    assert recognizer.language == "en-US"
