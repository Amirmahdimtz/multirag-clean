from typing import List

from sqlalchemy import select

from src.domain.models.chat_message import ChatMessage
from src.infrastructure.database.db_context import DbContext
from src.infrastructure.repositories.base_repository import BaseRepository


class ChatMessageRepository(BaseRepository[ChatMessage]):
    def __init__(self, db_context: DbContext) -> None:
        super().__init__(db_context)

    async def get_by_session_id(self, session_id: str) -> List[ChatMessage]:
        async with self.db_context.get_session() as session:
            result = await session.execute(
                select(ChatMessage).where(ChatMessage.session_id == session_id)
            )
            return list(result.scalars().all())
