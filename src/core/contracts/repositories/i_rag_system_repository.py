from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from src.domain.models.rag_system import RAGSystem


class IRAGSystemRepository(ABC):
    @abstractmethod
    async def add(self, rag_system: RAGSystem) -> RAGSystem:
        raise NotImplementedError

    @abstractmethod
    async def get_all(self) -> List[RAGSystem]:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, rag_system_id: UUID) -> Optional[RAGSystem]:
        raise NotImplementedError

    @abstractmethod
    async def update(self, rag_system: RAGSystem) -> RAGSystem:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, rag_system: RAGSystem) -> None:
        raise NotImplementedError
