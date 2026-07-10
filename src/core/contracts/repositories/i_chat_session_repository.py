from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from src.domain.models.chat_session import ChatSession


class IChatSessionRepository(ABC):
    @abstractmethod
    async def add(self, chat_session: ChatSession) -> ChatSession:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, chat_session_id: UUID) -> Optional[ChatSession]:
        raise NotImplementedError

    @abstractmethod
    async def get_by_user_id(self, user_id: UUID) -> List[ChatSession]:
        raise NotImplementedError

    @abstractmethod
    async def update(self, chat_session: ChatSession) -> ChatSession:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, chat_session: ChatSession) -> None:
        raise NotImplementedError
