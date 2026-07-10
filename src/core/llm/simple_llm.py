from typing import AsyncGenerator, List, Optional

from src.core.llm.base_llm import BaseLLM


class SimpleLLM(BaseLLM):
    async def generate(
        self,
        question: str,
        contexts: Optional[List[str]] = None,
    ) -> str:
        prompt = self.__build_prompt(question)

        return await self.chat_model_service.generate(prompt)

    async def stream(
        self,
        question: str,
        contexts: Optional[List[str]] = None,
    ) -> AsyncGenerator[str, None]:
        prompt = self.__build_prompt(question)

        async for token in self.chat_model_service.stream(prompt):
            yield token

    def __build_prompt(self, question: str) -> str:
        return f"""
You are a helpful assistant.

Answer the user's question clearly.
If the user writes in Persian, answer in Persian.
If the user writes in English, answer in English.

User message:
{question}

Answer:
""".strip()
