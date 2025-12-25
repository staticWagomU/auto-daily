"""OpenAI LLM client implementation."""

from openai import AsyncOpenAI

from auto_daily.config import get_openai_api_key, get_openai_model


class OpenAIClient:
    """Client for interacting with the OpenAI API.

    Implements the LLMClient protocol for use with the LLM abstraction layer.
    """

    def __init__(self, api_key: str | None = None, model: str | None = None) -> None:
        """Initialize the OpenAI client.

        Args:
            api_key: OpenAI API key.
                    Uses OPENAI_API_KEY env var if not specified.
            model: Model name to use (e.g., "gpt-4o-mini").
                  Uses OPENAI_MODEL env var or default if not specified.
        """
        self.api_key = api_key if api_key is not None else get_openai_api_key()
        self.model = model if model is not None else get_openai_model()
        self.client = AsyncOpenAI(api_key=self.api_key)

    async def generate(self, prompt: str, model: str) -> str:
        """Generate text using the OpenAI API.

        Args:
            prompt: The prompt to send to the model.
            model: Name of the model to use.

        Returns:
            Generated text response.
        """
        response = await self.client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
        )
        content = response.choices[0].message.content
        return content if content is not None else ""
