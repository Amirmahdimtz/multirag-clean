from typing import List, Optional

from sqlalchemy import select

from src.domain.models.dataset import Dataset
from src.infrastructure.database.db_context import DbContext
from src.infrastructure.repositories.base_repository import BaseRepository


class DatasetRepository(BaseRepository[Dataset]):
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
