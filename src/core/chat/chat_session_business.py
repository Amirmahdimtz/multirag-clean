from uuid import UUID

from src.core.exceptions.not_found_exception import NotFoundException
from src.domain.models.chat_session import ChatSession
from src.domain.enums.llm_type import LLMType


class ChatSessionBusiness:
    def __init__(self, chat_session_repository) -> None:
        self.chat_session_repository = chat_session_repository

    async def create_session(
        self,
        user_id: UUID,
        name: str,
        llm_type: str = "simple",
    ) -> ChatSession:
        session = ChatSession(
            user_id=user_id,
            name=name,
            llm_type=LLMType(llm_type),
        )

        return await self.chat_session_repository.add(session)

    async def get_user_sessions(self, user_id: UUID):
        return await self.chat_session_repository.get_by_user_id(user_id)

    async def get_by_id(self, session_id: UUID):
        session = await self.chat_session_repository.get_by_id(
            ChatSession,
            session_id,
        )

        if session is None:
            raise NotFoundException("Chat session not found")

        return session
