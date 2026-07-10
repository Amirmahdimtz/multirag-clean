from src.core.contracts.services.i_chat_model_service import IChatModelService
from src.core.llm.rag_llm import RAGLLM
from src.core.llm.simple_llm import SimpleLLM
from src.core.llm.user_rag_llm import UserRAGLLM


class LLMFactory:
    def __init__(self, chat_model_service: IChatModelService) -> None:
        self.chat_model_service = chat_model_service

    def create_simple_llm(self) -> SimpleLLM:
        return SimpleLLM(
            chat_model_service=self.chat_model_service,
        )

    def create_rag_llm(self) -> RAGLLM:
        return RAGLLM(
            chat_model_service=self.chat_model_service,
        )

    def create_user_rag_llm(self) -> UserRAGLLM:
        return UserRAGLLM(
            chat_model_service=self.chat_model_service,
        )
