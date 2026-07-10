from typing import List
from uuid import UUID

from src.core.contracts.repositories.i_chat_session_repository import (
    IChatSessionRepository,
)
from src.core.exceptions.not_found_exception import NotFoundException
from src.domain.enums.llm_type import LLMType
from src.domain.models.chat_session import ChatSession


class ChatSessionBusiness:
    def __init__(
        self,
        chat_session_repository: IChatSessionRepository,
    ) -> None:
        self.chat_session_repository = chat_session_repository

    async def create_session(
        self,
        user_id: UUID,
        name: str,
        llm_type: LLMType,
        rag_system_id: UUID | None = None,
        user_dataset_id: UUID | None = None,
    ) -> ChatSession:
        session = ChatSession(
            user_id=user_id,
            name=name,
            llm_type=llm_type,
            rag_system_id=rag_system_id,
            user_dataset_id=user_dataset_id,
        )

        return await self.chat_session_repository.add(session)

    async def get_user_sessions(self, user_id: UUID) -> List[ChatSession]:
        return await self.chat_session_repository.get_by_user_id(user_id)

    async def get_by_id(self, session_id: UUID) -> ChatSession:
        session = await self.chat_session_repository.get_by_id(
            session_id,
        )

        if session is None:
            raise NotFoundException("Chat session not found")

        return session

    async def update_last_active(self, session_id: UUID) -> ChatSession:
        session = await self.get_by_id(session_id)
        session.mark_as_active()

        return await self.chat_session_repository.update(session)

    async def delete_session(self, session_id: UUID) -> None:
        session = await self.get_by_id(session_id)
        await self.chat_session_repository.delete(session)
