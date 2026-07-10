from typing import List, Optional
from uuid import UUID

from sqlalchemy import select

from src.domain.models.user import User
from src.infrastructure.database.db_context import DbContext
from src.infrastructure.repositories.base_repository import BaseRepository
from src.core.contracts.repositories.i_user_repository import IUserRepository


class UserRepository(BaseRepository[User], IUserRepository):
    def __init__(self, db_context: DbContext) -> None:
        super().__init__(db_context)

    async def get_all(self) -> List[User]:
        async with self.db_context.get_session() as session:
            result = await session.execute(select(User))
            return list(result.scalars().all())

    async def get_by_username(self, username: str) -> Optional[User]:
        async with self.db_context.get_session() as session:
            result = await session.execute(
                select(User).where(User.username == username)
            )
            return result.scalar_one_or_none()

    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        return await super().get_by_id(User, user_id)
