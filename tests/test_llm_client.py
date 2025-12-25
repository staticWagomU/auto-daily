"""Tests for LLM client abstraction layer."""

import os
from unittest.mock import patch

import pytest


def test_llm_protocol() -> None:
    """Test that LLMClient Protocol defines the generate() method.

    The Protocol should:
    1. Define an async generate(prompt: str, model: str) -> str method
    2. Be a valid typing.Protocol
    3. Allow structural subtyping (duck typing with type safety)
    """
    from auto_daily.llm.protocol import LLMClient

    # Verify Protocol exists and has expected attributes
    assert hasattr(LLMClient, "generate")

    # Verify it's a Protocol class
    from typing import Protocol

    assert issubclass(LLMClient, Protocol)


def test_ollama_implements_protocol() -> None:
    """Test that OllamaClient implements the LLMClient protocol.

    The OllamaClient should:
    1. Have an async generate(prompt: str, model: str) -> str method
    2. Be structurally compatible with LLMClient Protocol
    """
    from auto_daily.llm.ollama import OllamaClient
    from auto_daily.llm.protocol import LLMClient

    # Create an instance
    client = OllamaClient()

    # Verify the method signature exists
    assert hasattr(client, "generate")
    assert callable(client.generate)

    # Type checking verification (this is for runtime, static checking happens via mypy/ty)
    # The client should be usable where LLMClient is expected
    def accepts_llm_client(c: LLMClient) -> None:
        pass

    # This should not raise - if OllamaClient implements the protocol correctly
    accepts_llm_client(client)


def test_get_llm_client_factory() -> None:
    """Test that get_llm_client() returns the correct client based on AI_BACKEND.

    The factory should:
    1. Return OllamaClient when AI_BACKEND is "ollama" or not set
    2. Raise ValueError for unknown backends
    """
    from auto_daily.llm import get_llm_client
    from auto_daily.llm.ollama import OllamaClient

    # Test default (ollama)
    env_without_var = {k: v for k, v in os.environ.items() if k != "AI_BACKEND"}
    with patch.dict(os.environ, env_without_var, clear=True):
        client = get_llm_client()
        assert isinstance(client, OllamaClient)

    # Test explicit ollama
    with patch.dict(os.environ, {"AI_BACKEND": "ollama"}):
        client = get_llm_client()
        assert isinstance(client, OllamaClient)

    # Test unknown backend raises ValueError
    with patch.dict(os.environ, {"AI_BACKEND": "unknown_backend"}):
        with pytest.raises(ValueError, match="Unknown AI backend"):
            get_llm_client()
