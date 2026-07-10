from typing import AsyncGenerator

from openai import AsyncOpenAI

from src.core.contracts.services.i_chat_model_service import IChatModelService


class VLLMChatModelService(IChatModelService):
    def __init__(
        self,
        model: str,
        base_url: str,
        api_key: str,
        temperature: float,
        max_tokens: int,
        top_p: float,
        top_k: int,
        timeout_seconds: float,
    ) -> None:
        if not model or not model.strip():
            raise ValueError("vLLM model name cannot be empty")

        if not api_key or not api_key.strip():
            raise ValueError("vLLM API key cannot be empty")

        if not base_url.startswith(("http://", "https://")):
            raise ValueError(
                "vLLM base URL must start with http:// or https://")

        if max_tokens <= 0:
            raise ValueError("vLLM max_tokens must be greater than zero")

        if timeout_seconds <= 0:
            raise ValueError("vLLM timeout_seconds must be greater than zero")

        if top_k <= 0:
            raise ValueError("vLLM top_k must be greater than zero")

        self._model_name = model.strip()
        self._temperature = temperature
        self._max_tokens = max_tokens
        self._top_p = top_p
        self._top_k = top_k
        self._client = AsyncOpenAI(
            api_key=api_key,
            base_url=base_url.rstrip("/"),
            timeout=timeout_seconds,
            max_retries=2,
        )

    async def generate(self, prompt: str) -> str:
        response = await self._client.chat.completions.create(
            model=self._model_name,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            temperature=self._temperature,
            max_tokens=self._max_tokens,
            top_p=self._top_p,
            extra_body={"top_k": self._top_k},
        )

        return response.choices[0].message.content or ""

    async def stream(self, prompt: str) -> AsyncGenerator[str, None]:
        stream = await self._client.chat.completions.create(
            model=self._model_name,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            temperature=self._temperature,
            max_tokens=self._max_tokens,
            top_p=self._top_p,
            extra_body={"top_k": self._top_k},
            stream=True,
        )

        async for chunk in stream:
            if not chunk.choices:
                continue

            content = chunk.choices[0].delta.content

            if content:
                yield content
