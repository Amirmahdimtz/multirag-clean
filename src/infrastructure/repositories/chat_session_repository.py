from typing import List

from sqlalchemy import select

from src.domain.models.chat_session import ChatSession
from src.infrastructure.database.db_context import DbContext
from src.infrastructure.repositories.base_repository import BaseRepository


class ChatSessionRepository(BaseRepository[ChatSession]):
    def __init__(self, db_context: DbContext) -> None:
        super().__init__(db_context)

    async def get_by_user_id(self, user_id: str) -> List[ChatSession]:
        async with self.db_context.get_session() as session:
            result = await session.execute(
                select(ChatSession).where(ChatSession.user_id == user_id)
            )
            return list(result.scalars().all())
