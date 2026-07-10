from typing import AsyncGenerator, List, Optional

from src.core.llm.base_llm import BaseLLM


class UserRAGLLM(BaseLLM):
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

    async def stream(
        self,
        question: str,
        contexts: Optional[List[str]] = None,
    ) -> AsyncGenerator[str, None]:
        prompt = self.__build_prompt(
            question=question,
            contexts=contexts or [],
        )

        async for token in self.chat_model_service.stream(prompt):
            yield token

    def __build_prompt(
        self,
        question: str,
        contexts: List[str],
    ) -> str:
        joined_contexts = "\n\n".join(contexts).strip()

        if not joined_contexts:
            joined_contexts = "NO_USER_DOCUMENT_CONTEXT_PROVIDED"

        return f"""
You are a private user-document RAG assistant.

Your task:
- Answer the user's question using ONLY the retrieved context from the authenticated user's uploaded documents.
- Treat all retrieved context as private user-owned document content.
- Do not use admin/global RAG knowledge.
- Do not use outside knowledge.
- Do not invent facts, names, numbers, dates, URLs, or explanations.
- If the answer is not clearly available in the user's uploaded documents, say in Persian:
"پاسخ این سؤال در اسناد آپلودشده‌ی شما پیدا نشد."
- If the question is in Persian, answer in Persian.
- If the question is in English, answer in English.
- Keep the answer clear and concise.
- When useful, mention the relevant chunk references like [chunk: 3].
- Do not mention similarity scores unless the user asks.

Retrieved user document context:
{joined_contexts}

User question:
{question}

Final answer:
""".strip()
