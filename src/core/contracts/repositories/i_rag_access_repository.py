from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from src.domain.models.rag_access import RAGAccess
from src.domain.models.rag_system import RAGSystem
from src.domain.models.user import User


class IRAGAccessRepository(ABC):
    @abstractmethod
    async def add(self, rag_access: RAGAccess) -> RAGAccess:
        raise NotImplementedError

    @abstractmethod
    async def get_by_user_and_rag_system(
        self,
        user_id: UUID,
        rag_system_id: UUID,
    ) -> Optional[RAGAccess]:
        raise NotImplementedError

    @abstractmethod
    async def exists(
        self,
        user_id: UUID,
        rag_system_id: UUID,
    ) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def get_users_by_rag_system_id(
        self,
        rag_system_id: UUID,
    ) -> List[User]:
        raise NotImplementedError

    @abstractmethod
    async def get_rag_systems_by_user_id(
        self,
        user_id: UUID,
    ) -> List[RAGSystem]:
        raise NotImplementedError

    @abstractmethod
    async def remove_by_user_and_rag_system(
        self,
        user_id: UUID,
        rag_system_id: UUID,
    ) -> bool:
        raise NotImplementedError
