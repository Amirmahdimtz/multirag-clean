from typing import Generic, Optional, TypeVar

from src.infrastructure.database.db_context import DbContext

T = TypeVar("T")


class BaseRepository(Generic[T]):
    def __init__(self, db_context: DbContext) -> None:
        self.db_context = db_context

    async def add(self, entity: T) -> T:
        async with self.db_context.get_session() as session:
            session.add(entity)
            await session.commit()
            await session.refresh(entity)
            return entity

    async def get_by_id(self, model: type[T], id) -> Optional[T]:
        async with self.db_context.get_session() as session:
            return await session.get(model, id)

    async def delete(self, entity: T) -> None:
        async with self.db_context.get_session() as session:
            await session.delete(entity)
            await session.commit()
