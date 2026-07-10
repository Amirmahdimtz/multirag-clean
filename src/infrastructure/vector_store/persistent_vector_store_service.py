import math
from typing import List
from uuid import UUID

from sqlalchemy import delete, select

from src.domain.models.vector_document import VectorDocument
from src.infrastructure.database.db_context import DbContext
from src.infrastructure.vector_store.vector_document_record import (
    VectorDocumentRecord,
)
from src.infrastructure.vector_store.vector_search_result import (
    VectorSearchResult,
)
from src.core.contracts.services.i_vector_store_service import IVectorStoreService


class PersistentVectorStoreService(IVectorStoreService):
    def __init__(self, db_context: DbContext) -> None:
        self.db_context = db_context

    async def upsert_documents(
        self,
        dataset_id: UUID,
        documents: List[VectorDocument],
    ) -> int:
        async with self.db_context.get_session() as session:
            await session.execute(
                delete(VectorDocumentRecord).where(
                    VectorDocumentRecord.dataset_id == str(dataset_id)
                )
            )

            records = [
                VectorDocumentRecord(
                    dataset_id=str(document.dataset_id),
                    chunk_index=document.chunk_index,
                    content=document.content,
                    embedding=document.embedding,
                    metadata_json=document.metadata,
                )
                for document in documents
            ]

            session.add_all(records)
            await session.commit()

            return len(records)

    async def similarity_search(
        self,
        dataset_id: UUID,
        query_embedding: List[float],
        limit: int,
        score_threshold: float | None = None,
    ) -> List[VectorSearchResult]:
        async with self.db_context.get_session() as session:
            result = await session.execute(
                select(VectorDocumentRecord).where(
                    VectorDocumentRecord.dataset_id == str(dataset_id)
                )
            )

            records = list(result.scalars().all())

        scored_results: list[VectorSearchResult] = []

        for record in records:
            document = self.__to_vector_document(record)

            score = self.__cosine_similarity(
                query_embedding,
                document.embedding,
            )

            if score_threshold is not None and score < score_threshold:
                continue

            scored_results.append(
                VectorSearchResult(
                    document=document,
                    score=score,
                )
            )

        scored_results.sort(
            key=lambda item: item.score,
            reverse=True,
        )

        return scored_results[:limit]

    async def delete_dataset(self, dataset_id: UUID) -> None:
        async with self.db_context.get_session() as session:
            await session.execute(
                delete(VectorDocumentRecord).where(
                    VectorDocumentRecord.dataset_id == str(dataset_id)
                )
            )
            await session.commit()

    async def count_documents(self, dataset_id: UUID) -> int:
        async with self.db_context.get_session() as session:
            result = await session.execute(
                select(VectorDocumentRecord).where(
                    VectorDocumentRecord.dataset_id == str(dataset_id)
                )
            )

            records = list(result.scalars().all())
            return len(records)

    def __to_vector_document(
        self,
        record: VectorDocumentRecord,
    ) -> VectorDocument:
        return VectorDocument(
            dataset_id=UUID(record.dataset_id),
            chunk_index=record.chunk_index,
            content=record.content,
            embedding=record.embedding,
            metadata=record.metadata_json or {},
        )

    def __cosine_similarity(
        self,
        vector_a: List[float],
        vector_b: List[float],
    ) -> float:
        if len(vector_a) != len(vector_b):
            raise ValueError(
                f"Vector dimension mismatch. "
                f"Query vector has {len(vector_a)} dimensions, "
                f"stored vector has {len(vector_b)} dimensions. "
                f"Please re-vectorize the dataset with the active embedding provider."
            )

        dot_product = sum(a * b for a, b in zip(vector_a, vector_b))
        norm_a = math.sqrt(sum(a * a for a in vector_a))
        norm_b = math.sqrt(sum(b * b for b in vector_b))

        if norm_a == 0 or norm_b == 0:
            return 0.0

        return dot_product / (norm_a * norm_b)
