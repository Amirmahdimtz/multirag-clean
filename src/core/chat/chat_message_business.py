from typing import List
from uuid import UUID

from src.domain.models.chat_message import ChatMessage
from src.domain.enums.message_role import MessageRole


class ChatMessageBusiness:
    def __init__(
        self,
        chat_message_repository,
    ) -> None:
        self.chat_message_repository = chat_message_repository

    async def add_message(
        self,
        session_id: UUID,
        role: str,
        content: str,
    ) -> ChatMessage:
        message = ChatMessage(
            session_id=session_id,
            role=MessageRole(role),
            content=content,
        )

        return await self.chat_message_repository.add(message)

    async def get_session_messages(self, session_id: UUID) -> List[ChatMessage]:
        return await self.chat_message_repository.get_by_session_id(
            session_id,
        )
