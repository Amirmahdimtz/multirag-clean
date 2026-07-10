from abc import ABC, abstractmethod
from typing import List
from uuid import UUID

from src.domain.models.vector_document import VectorDocument
from src.domain.models.vector_search_result import VectorSearchResult


class IVectorStoreService(ABC):
    @abstractmethod
    async def upsert_documents(
        self,
        dataset_id: UUID,
        documents: List[VectorDocument],
    ) -> int:
        raise NotImplementedError

    @abstractmethod
    async def similarity_search(
        self,
        dataset_id: UUID,
        query_embedding: List[float],
        limit: int,
        score_threshold: float | None = None,
    ) -> List[VectorSearchResult]:
        raise NotImplementedError

    @abstractmethod
    async def delete_dataset(self, dataset_id: UUID) -> None:
        raise NotImplementedError

    @abstractmethod
    async def count_documents(self, dataset_id: UUID) -> int:
        raise NotImplementedError
