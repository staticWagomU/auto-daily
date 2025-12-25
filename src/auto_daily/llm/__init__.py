"""LLM client abstraction layer.

This module provides a unified interface for interacting with different LLM backends.
"""

from auto_daily.config import get_ai_backend
from auto_daily.llm.ollama import OllamaClient
from auto_daily.llm.openai import OpenAIClient
from auto_daily.llm.protocol import LLMClient

__all__ = ["LLMClient", "OllamaClient", "OpenAIClient", "get_llm_client"]


def get_llm_client() -> LLMClient:
    """Get the LLM client based on the AI_BACKEND environment variable.

    Returns an instance of the appropriate LLM client based on the configured backend.

    Returns:
        An LLM client instance implementing the LLMClient protocol.

    Raises:
        ValueError: If the configured backend is not supported.
    """
    backend = get_ai_backend()

    if backend == "ollama":
        return OllamaClient()

    if backend == "openai":
        return OpenAIClient()

    raise ValueError(f"Unknown AI backend: {backend}")
