from typing import Generic, TypeVar, Optional, List
from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar("T")


class BaseRepository(Generic[T]):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add(self, entity: T) -> T:
        self.session.add(entity)
        await self.session.commit()
        await self.session.refresh(entity)
        return entity

    async def get_by_id(self, model: type[T], id: str) -> Optional[T]:
        return await self.session.get(model, id)

    async def delete(self, entity: T) -> None:
        await self.session.delete(entity)
        await self.session.commit()
