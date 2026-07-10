import asyncio
from typing import AsyncGenerator

from src.core.contracts.services.i_chat_model_service import IChatModelService


class FakeChatModelService(IChatModelService):
    async def generate(self, prompt: str) -> str:
        return (
            "این پاسخ توسط FakeChatModelService تولید شده است.\n\n"
            "این نسخه فقط برای تست معماری Streaming است و بعداً با LLM واقعی "
            "مثل Ollama یا OpenAI جایگزین می‌شود.\n\n"
            f"Prompt received:\n{prompt[:500]}"
        )

    async def stream(self, prompt: str) -> AsyncGenerator[str, None]:
        response = await self.generate(prompt)

        for word in response.split():
            yield word + " "
            await asyncio.sleep(0.05)
