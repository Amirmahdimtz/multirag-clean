from abc import ABC, abstractmethod
from typing import List, Optional

from src.core.contracts.services.i_chat_model_service import IChatModelService


class BaseLLM(ABC):
    def __init__(self, chat_model_service: IChatModelService) -> None:
        self.chat_model_service = chat_model_service

    @abstractmethod
    async def generate(
        self,
        question: str,
        contexts: Optional[List[str]] = None,
    ) -> str:
        raise NotImplementedError
