from typing import List, Optional
from uuid import UUID

from sqlalchemy import select

from src.core.contracts.repositories.i_dataset_repository import IDatasetRepository
from src.domain.enums.dataset_scope import DatasetScope
from src.domain.models.dataset import Dataset
from src.infrastructure.database.db_context import DbContext
from src.infrastructure.repositories.base_repository import BaseRepository


class DatasetRepository(BaseRepository[Dataset], IDatasetRepository):
    model = Dataset

    def __init__(self, db_context: DbContext) -> None:
        super().__init__(db_context)

    async def get_all(self) -> List[Dataset]:
        async with self.db_context.get_session() as session:
            result = await session.execute(select(Dataset))
            return list(result.scalars().all())

    async def get_by_name(self, name: str) -> Optional[Dataset]:
        async with self.db_context.get_session() as session:
            result = await session.execute(
                select(Dataset).where(Dataset.name == name)
            )
            return result.scalar_one_or_none()

    async def get_by_scope(self, scope: DatasetScope) -> List[Dataset]:
        async with self.db_context.get_session() as session:
            result = await session.execute(
                select(Dataset).where(Dataset.scope == scope)
            )
            return list(result.scalars().all())

    async def get_by_owner_user_id(self, owner_user_id: UUID) -> List[Dataset]:
        async with self.db_context.get_session() as session:
            result = await session.execute(
                select(Dataset).where(
                    Dataset.scope == DatasetScope.USER,
                    Dataset.owner_user_id == owner_user_id,
                )
            )
            return list(result.scalars().all())

    async def get_by_id(self, dataset_id: UUID) -> Optional[Dataset]:
        return await super().get_by_id(Dataset, dataset_id)
