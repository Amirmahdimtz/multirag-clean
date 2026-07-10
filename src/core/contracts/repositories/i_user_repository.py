from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from src.domain.models.user import User


class IUserRepository(ABC):
    @abstractmethod
    async def add(self, user: User) -> User:
        raise NotImplementedError

    @abstractmethod
    async def get_all(self) -> List[User]:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        raise NotImplementedError

    @abstractmethod
    async def get_by_username(self, username: str) -> Optional[User]:
        raise NotImplementedError

    @abstractmethod
    async def update(self, user: User) -> User:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, user: User) -> None:
        raise NotImplementedError
