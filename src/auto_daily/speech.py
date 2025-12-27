"""Speech recognition module using Apple Speech Framework (PBI-046c).

This module provides real-time speech-to-text functionality using
macOS's Speech Framework (SFSpeechRecognizer) and AVFoundation
(AVAudioEngine) for microphone input.
"""

import threading
from collections.abc import Callable
from typing import Any

from AVFoundation import AVAudioEngine  # type: ignore[import-untyped]
from Foundation import NSLocale  # type: ignore[import-untyped]
from Speech import (  # type: ignore[import-untyped]
    SFSpeechAudioBufferRecognitionRequest,
    SFSpeechRecognizer,
)


class SpeechRecognizer:
    """Real-time speech recognizer using Apple Speech Framework.

    This class wraps macOS's SFSpeechRecognizer to provide a simple
    interface for speech-to-text conversion from microphone input.

    Attributes:
        _on_result: Callback function invoked with recognition results.
        _language: Language code for speech recognition (e.g., "ja-JP").
        _lock: Threading lock for thread-safe state management.
    """

    def __init__(
        self,
        on_result: Callable[[str, float, bool], None],
        language: str = "ja-JP",
    ) -> None:
        """Initialize the SpeechRecognizer.

        Args:
            on_result: Callback function that receives (transcript, confidence, is_final).
            language: Language code for recognition (default: "ja-JP").
        """
        self._on_result = on_result
        self._language = language
        self._lock = threading.Lock()
        self._running = False

        # macOS API objects (initialized on start)
        self._recognizer: Any = None
        self._audio_engine: Any = None
        self._request: Any = None
        self._recognition_task: Any = None

    @property
    def language(self) -> str:
        """Return the configured language code."""
        return self._language

    def is_running(self) -> bool:
        """Check if speech recognition is currently running.

        Returns:
            True if recognition is active, False otherwise.
        """
        with self._lock:
            return self._running

    def start(self) -> None:
        """Start speech recognition from microphone input.

        This method initializes the audio engine and speech recognizer,
        then begins capturing and recognizing speech.

        Raises:
            RuntimeError: If speech recognizer is not available.
        """
        with self._lock:
            if self._running:
                return

            # Initialize macOS Speech Framework objects
            locale = NSLocale.alloc().initWithLocaleIdentifier_(self._language)
            self._recognizer = SFSpeechRecognizer.alloc().initWithLocale_(locale)

            if not self._recognizer.isAvailable():
                raise RuntimeError("Speech recognizer is not available")

            # Initialize audio engine
            self._audio_engine = AVAudioEngine.alloc().init()

            # Create recognition request
            self._request = SFSpeechAudioBufferRecognitionRequest.alloc().init()
            self._request.setShouldReportPartialResults_(True)

            # Get input node and format
            input_node = self._audio_engine.inputNode()
            record_format = input_node.outputFormatForBus_(0)

            # Install tap on input node to capture audio
            def handle_buffer(buffer: Any, when: Any) -> None:
                self._request.appendAudioPCMBuffer_(buffer)

            input_node.installTapOnBus_bufferSize_format_block_(
                0, 1024, record_format, handle_buffer
            )

            # Start recognition task
            def handle_recognition(result: Any, error: Any) -> None:
                if result is not None:
                    transcript = result.bestTranscription().formattedString()
                    # Calculate confidence as average of segments
                    segments = result.bestTranscription().segments()
                    if segments and len(segments) > 0:
                        total_confidence = sum(seg.confidence() for seg in segments)
                        confidence = total_confidence / len(segments)
                    else:
                        confidence = 0.0
                    is_final = result.isFinal()
                    self._handle_result(transcript, confidence, is_final)

            self._recognition_task = (
                self._recognizer.recognitionTaskWithRequest_resultHandler_(
                    self._request, handle_recognition
                )
            )

            # Start audio engine
            self._audio_engine.prepare()
            self._audio_engine.startAndReturnError_(None)

            self._running = True

    def stop(self) -> None:
        """Stop speech recognition.

        This method stops the audio engine and cancels any ongoing
        recognition task. Safe to call even if not running.
        """
        with self._lock:
            if not self._running:
                return

            # Stop audio engine
            if self._audio_engine is not None:
                input_node = self._audio_engine.inputNode()
                input_node.removeTapOnBus_(0)
                self._audio_engine.stop()

            # End recognition request
            if self._request is not None:
                self._request.endAudio()

            # Cancel recognition task
            if self._recognition_task is not None:
                self._recognition_task.cancel()

            # Clear references
            self._recognizer = None
            self._audio_engine = None
            self._request = None
            self._recognition_task = None

            self._running = False

    def _handle_result(
        self, transcript: str, confidence: float, is_final: bool
    ) -> None:
        """Handle a recognition result by invoking the callback.

        Args:
            transcript: The recognized text.
            confidence: Confidence score (0.0-1.0).
            is_final: Whether this is a final result.
        """
        self._on_result(transcript, confidence, is_final)
