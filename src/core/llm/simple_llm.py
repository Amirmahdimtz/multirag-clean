from typing import List, Optional

from src.core.llm.base_llm import BaseLLM


class SimpleLLM(BaseLLM):
    async def generate(
        self,
        question: str,
        contexts: Optional[List[str]] = None,
    ) -> str:
        prompt = self.__build_prompt(question)

        return await self.chat_model_service.generate(prompt)

    def __build_prompt(self, question: str) -> str:
        return f"""
You are a helpful assistant.
Answer the user's question clearly.

QUESTION:
{question}
""".strip()
