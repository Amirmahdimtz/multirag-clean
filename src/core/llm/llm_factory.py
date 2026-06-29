from src.core.llm.base_chat_model_service import BaseChatModelService
from src.core.llm.rag_llm import RAGLLM
from src.core.llm.simple_llm import SimpleLLM


class LLMFactory:
    def __init__(self, chat_model_service: BaseChatModelService) -> None:
        self.chat_model_service = chat_model_service

    def create_simple_llm(self) -> SimpleLLM:
        return SimpleLLM(
            chat_model_service=self.chat_model_service,
        )

    def create_rag_llm(self) -> RAGLLM:
        return RAGLLM(
            chat_model_service=self.chat_model_service,
        )
