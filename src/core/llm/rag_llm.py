from typing import List, Optional

from src.core.llm.base_llm import BaseLLM


class RAGLLM(BaseLLM):
    async def generate(
        self,
        question: str,
        contexts: Optional[List[str]] = None,
    ) -> str:
        prompt = self.__build_prompt(
            question=question,
            contexts=contexts or [],
        )

        return await self.chat_model_service.generate(prompt)

    def __build_prompt(
        self,
        question: str,
        contexts: List[str],
    ) -> str:
        joined_contexts = "\n\n---\n\n".join(contexts)

        return f"""
You are a retrieval-augmented assistant.

Use ONLY the provided context to answer the question.
If the answer is not available in the context, say:
"I could not find the answer in the provided documents."

CONTEXT:
{joined_contexts}

QUESTION:
{question}

ANSWER:
""".strip()
