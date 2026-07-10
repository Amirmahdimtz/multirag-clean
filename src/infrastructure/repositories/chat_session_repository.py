from typing import List, Optional
from uuid import UUID

from sqlalchemy import select

from src.domain.models.chat_session import ChatSession
from src.infrastructure.database.db_context import DbContext
from src.infrastructure.repositories.base_repository import BaseRepository
from src.core.contracts.repositories.i_chat_session_repository import (
    IChatSessionRepository,
)


class ChatSessionRepository(
    BaseRepository[ChatSession],
    IChatSessionRepository,
):
    def __init__(self, db_context: DbContext) -> None:
        super().__init__(db_context)

    async def get_by_id(
        self,
        chat_session_id: UUID,
    ) -> Optional[ChatSession]:
        return await super().get_by_id(
            ChatSession,
            chat_session_id,
        )

    async def get_by_user_id(self, user_id: UUID) -> List[ChatSession]:
        async with self.db_context.get_session() as session:
            result = await session.execute(
                select(ChatSession).where(ChatSession.user_id == user_id)
            )

            return list(result.scalars().all())
