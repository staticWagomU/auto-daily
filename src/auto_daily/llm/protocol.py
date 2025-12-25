"""Protocol definition for LLM clients."""

from typing import Protocol, runtime_checkable


@runtime_checkable
class LLMClient(Protocol):
    """Protocol for LLM client implementations.

    This protocol defines the interface that all LLM clients must implement.
    Uses structural subtyping (duck typing with type safety).
    """

    async def generate(self, prompt: str, model: str) -> str:
        """Generate text using the LLM.

        Args:
            prompt: The prompt to send to the model.
            model: Name of the model to use.

        Returns:
            Generated text response.
        """
        ...
