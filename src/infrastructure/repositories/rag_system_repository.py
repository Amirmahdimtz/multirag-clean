from typing import List, Optional
from uuid import UUID

from sqlalchemy import select

from src.domain.models.rag_system import RAGSystem
from src.infrastructure.database.db_context import DbContext
from src.infrastructure.repositories.base_repository import BaseRepository
from src.core.contracts.repositories.i_rag_system_repository import IRAGSystemRepository


class RAGSystemRepository(BaseRepository[RAGSystem], IRAGSystemRepository):
    model = RAGSystem

    def __init__(self, db_context: DbContext) -> None:
        super().__init__(db_context)

    async def get_all(self) -> List[RAGSystem]:
        async with self.db_context.get_session() as session:
            result = await session.execute(select(RAGSystem))
            return list(result.scalars().all())

    async def get_by_id(self, rag_system_id: UUID) -> Optional[RAGSystem]:
        return await super().get_by_id(RAGSystem, rag_system_id)
