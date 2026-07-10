from typing import List, Optional
from uuid import UUID

from sqlalchemy import delete, exists, select

from src.core.contracts.repositories.i_rag_access_repository import IRAGAccessRepository
from src.domain.models.rag_access import RAGAccess
from src.domain.models.rag_system import RAGSystem
from src.domain.models.user import User
from src.infrastructure.database.db_context import DbContext
from src.infrastructure.repositories.base_repository import BaseRepository


class RAGAccessRepository(BaseRepository[RAGAccess], IRAGAccessRepository):
    def __init__(self, db_context: DbContext) -> None:
        super().__init__(db_context)

    async def get_by_user_and_rag_system(
        self,
        user_id: UUID,
        rag_system_id: UUID,
    ) -> Optional[RAGAccess]:
        async with self.db_context.get_session() as session:
            result = await session.execute(
                select(RAGAccess).where(
                    RAGAccess.user_id == user_id,
                    RAGAccess.rag_system_id == rag_system_id,
                )
            )

            return result.scalar_one_or_none()

    async def exists(
        self,
        user_id: UUID,
        rag_system_id: UUID,
    ) -> bool:
        async with self.db_context.get_session() as session:
            result = await session.execute(
                select(
                    exists().where(
                        RAGAccess.user_id == user_id,
                        RAGAccess.rag_system_id == rag_system_id,
                    )
                )
            )

            return bool(result.scalar())

    async def get_users_by_rag_system_id(
        self,
        rag_system_id: UUID,
    ) -> List[User]:
        async with self.db_context.get_session() as session:
            result = await session.execute(
                select(User)
                .join(RAGAccess, RAGAccess.user_id == User.id)
                .where(RAGAccess.rag_system_id == rag_system_id)
                .order_by(User.username)
            )

            return list(result.scalars().all())

    async def get_rag_systems_by_user_id(
        self,
        user_id: UUID,
    ) -> List[RAGSystem]:
        async with self.db_context.get_session() as session:
            result = await session.execute(
                select(RAGSystem)
                .join(RAGAccess, RAGAccess.rag_system_id == RAGSystem.id)
                .where(RAGAccess.user_id == user_id)
                .order_by(RAGSystem.name)
            )

            return list(result.scalars().all())

    async def remove_by_user_and_rag_system(
        self,
        user_id: UUID,
        rag_system_id: UUID,
    ) -> bool:
        async with self.db_context.get_session() as session:
            result = await session.execute(
                delete(RAGAccess).where(
                    RAGAccess.user_id == user_id,
                    RAGAccess.rag_system_id == rag_system_id,
                )
            )

            await session.commit()

            return result.rowcount > 0
