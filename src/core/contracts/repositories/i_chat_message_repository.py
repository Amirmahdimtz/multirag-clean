from abc import ABC, abstractmethod
from typing import List
from uuid import UUID

from src.domain.models.chat_message import ChatMessage


class IChatMessageRepository(ABC):
    @abstractmethod
    async def add(self, chat_message: ChatMessage) -> ChatMessage:
        raise NotImplementedError

    @abstractmethod
    async def get_by_session_id(
        self,
        session_id: UUID,
    ) -> List[ChatMessage]:
        raise NotImplementedError

    @abstractmethod
    async def delete_by_session_id(self, session_id: UUID) -> None:
        raise NotImplementedError
