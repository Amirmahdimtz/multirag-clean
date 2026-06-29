import math
from typing import Dict, List
from uuid import UUID

from src.domain.models.vector_document import VectorDocument
from src.infrastructure.vector_store.vector_search_result import VectorSearchResult


class InMemoryVectorStoreService:
    def __init__(self) -> None:
        self.documents_by_dataset: Dict[str, List[VectorDocument]] = {}

    def upsert_documents(
        self,
        dataset_id: UUID,
        documents: List[VectorDocument],
    ) -> int:
        dataset_key = str(dataset_id)
        self.documents_by_dataset[dataset_key] = documents

        return len(documents)

    def similarity_search(
        self,
        dataset_id: UUID,
        query_embedding: List[float],
        limit: int = 5,
    ) -> List[VectorSearchResult]:
        dataset_key = str(dataset_id)
        documents = self.documents_by_dataset.get(dataset_key, [])

        results = [
            VectorSearchResult(
                document=document,
                score=self.__cosine_similarity(
                    query_embedding,
                    document.embedding,
                ),
            )
            for document in documents
        ]

        results.sort(key=lambda item: item.score, reverse=True)

        return results[:limit]

    def delete_dataset(self, dataset_id: UUID) -> None:
        dataset_key = str(dataset_id)
        self.documents_by_dataset.pop(dataset_key, None)

    def count_documents(self, dataset_id: UUID) -> int:
        dataset_key = str(dataset_id)
        return len(self.documents_by_dataset.get(dataset_key, []))

    def __cosine_similarity(
        self,
        vector_a: List[float],
        vector_b: List[float],
    ) -> float:
        if len(vector_a) != len(vector_b):
            raise ValueError("Vectors must have the same dimension")

        dot_product = sum(a * b for a, b in zip(vector_a, vector_b))
        norm_a = math.sqrt(sum(a * a for a in vector_a))
        norm_b = math.sqrt(sum(b * b for b in vector_b))

        if norm_a == 0 or norm_b == 0:
            return 0.0

        return dot_product / (norm_a * norm_b)
