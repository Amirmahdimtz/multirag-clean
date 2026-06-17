from typing import List
from uuid import UUID

from src.domain.models.user import User


class UserBusiness:
    def __init__(self, user_repository) -> None:
        self.user_repository = user_repository

    async def create_user(self, username: str) -> User:
        user = User(username=username)
        return await self.user_repository.add(user)

    async def get_all_users(self) -> List[User]:
        return await self.user_repository.get_all()

    async def get_user_by_id(self, user_id: UUID):
        return await self.user_repository.get_by_id(User, str(user_id))

    async def delete_user(self, user: User):
        return await self.user_repository.delete(user)
