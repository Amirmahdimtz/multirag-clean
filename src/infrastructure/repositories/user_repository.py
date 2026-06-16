from typing import List, Optional
from sqlalchemy import select

from src.domain.models.user import User
from src.infrastructure.database.db_context import DbContext
from src.infrastructure.repositories.base_repository import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self, db_context: DbContext) -> None:
        super().__init__(db_context.get_session())

    async def get_all(self) -> List[User]:
        result = await self.session.execute(select(User))
        return result.scalars().all()

    async def get_by_username(self, username: str) -> Optional[User]:
        result = await self.session.execute(
            select(User).where(User.username == username)
        )
        return result.scalar_one_or_none()
