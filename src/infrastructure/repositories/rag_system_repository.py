from typing import List

from sqlalchemy import select

from src.domain.models.rag_system import RAGSystem
from src.infrastructure.database.db_context import DbContext
from src.infrastructure.repositories.base_repository import BaseRepository


class RAGSystemRepository(BaseRepository[RAGSystem]):
    def __init__(self, db_context: DbContext) -> None:
        super().__init__(db_context)

    async def get_all(self) -> List[RAGSystem]:
        async with self.db_context.get_session() as session:
            result = await session.execute(select(RAGSystem))
            return list(result.scalars().all())
