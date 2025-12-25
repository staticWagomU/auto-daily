"""LM Studio LLM client implementation."""

from openai import AsyncOpenAI


class LMStudioClient:
    """Client for interacting with the LM Studio API.

    Implements the LLMClient protocol for use with the LLM abstraction layer.
    LM Studio provides an OpenAI-compatible API, so we use the OpenAI SDK
    with a custom base URL.
    """

    def __init__(self, base_url: str | None = None, model: str | None = None) -> None:
        """Initialize the LM Studio client.

        Args:
            base_url: LM Studio server URL.
                     Uses LM_STUDIO_BASE_URL env var or "http://localhost:1234" if not specified.
            model: Model name to use.
                  Uses LM_STUDIO_MODEL env var or "default" if not specified.
        """
        from auto_daily.config import get_lm_studio_base_url, get_lm_studio_model

        self.base_url = base_url if base_url is not None else get_lm_studio_base_url()
        self.model = model if model is not None else get_lm_studio_model()
        self.client = AsyncOpenAI(
            base_url=f"{self.base_url}/v1",
            api_key="not-needed",  # LM Studio doesn't require an API key
        )

    async def generate(self, prompt: str, model: str) -> str:
        """Generate text using the LM Studio API.

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
