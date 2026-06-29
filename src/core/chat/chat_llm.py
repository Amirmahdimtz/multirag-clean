from src.core.chat.chat_history_service import ChatHistoryService
from src.core.llm.llm_factory import LLMFactory


class ChatLLM:
    def __init__(
        self,
        llm_factory: LLMFactory,
        chat_history_service: ChatHistoryService,
    ) -> None:
        self.llm_factory = llm_factory
        self.chat_history_service = chat_history_service

    async def generate(
        self,
        question: str,
        contexts: list[str],
        history_messages: list,
    ) -> str:
        history_text = self.chat_history_service.build_history_text(
            history_messages
        )

        full_question = f"""
CHAT HISTORY:
{history_text}

CURRENT QUESTION:
{question}
""".strip()

        rag_llm = self.llm_factory.create_rag_llm()

        return await rag_llm.generate(
            question=full_question,
            contexts=contexts,
        )
