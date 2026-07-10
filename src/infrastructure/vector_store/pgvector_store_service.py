from __future__ import annotations

from sqlalchemy import text

import re
from typing import Dict, List
from uuid import UUID

from langchain_core.documents import Document
from langchain_postgres import PGEngine, PGVectorStore
from langchain_postgres.v2.indexes import DistanceStrategy, HNSWIndex

from src.core.contracts.services.i_embedding_service import IEmbeddingService
from src.core.contracts.services.i_vector_store_service import IVectorStoreService
from src.domain.models.vector_document import VectorDocument
from src.domain.models.vector_search_result import VectorSearchResult
from src.infrastructure.database.db_context import DbContext
from src.infrastructure.vector_store.langchain_embedding_adapter import (
    LangChainEmbeddingAdapter,
)


class PGVectorStoreService(IVectorStoreService):
    def __init__(
        self,
        db_context: DbContext,
        embedding_service: IEmbeddingService,
        table_prefix: str,
        vector_size: int,
        batch_size: int = 10,
        hnsw_enabled: bool = True,
    ) -> None:
        if vector_size != embedding_service.dimension:
            raise ValueError(
                "PGVector dimension must match the active embedding dimension. "
                f"PGVector={vector_size}, embedding={embedding_service.dimension}"
            )

        if batch_size <= 0:
            raise ValueError("PGVector batch size must be greater than zero")

        self._db_context = db_context
        self._embedding_service = embedding_service
        self._embedding_adapter = LangChainEmbeddingAdapter(
            embedding_service=embedding_service,
        )

        self._pg_engine = PGEngine.from_engine(
            engine=db_context.engine,
        )

        self._table_prefix = self.__sanitize_identifier(table_prefix)
        self._vector_size = vector_size
        self._batch_size = batch_size
        self._hnsw_enabled = hnsw_enabled

        self._stores: Dict[str, PGVectorStore] = {}

    async def upsert_documents(
        self,
        dataset_id: UUID,
        documents: List[VectorDocument],
    ) -> int:
        table_name = self.__build_table_name(dataset_id)

        await self.__drop_table_if_exists(table_name)
        await self.__initialize_table(table_name)

        store = await self.__get_store(table_name)

        for batch in self.__batch(documents, self._batch_size):
            texts = [
                self.__sanitize_text(document.content)
                for document in batch
            ]

            embeddings = [
                document.embedding
                for document in batch
            ]

            metadatas = [
                self.__build_metadata(document)
                for document in batch
            ]

            ids = [
                str(document.id)
                for document in batch
            ]

            await store.aadd_embeddings(
                texts=texts,
                embeddings=embeddings,
                metadatas=metadatas,
                ids=ids,
            )

        if self._hnsw_enabled and documents:
            await self.__apply_hnsw_index(store, table_name)

        return len(documents)

    async def similarity_search(
        self,
        dataset_id: UUID,
        query_embedding: List[float],
        limit: int,
        score_threshold: float | None = None,
    ) -> List[VectorSearchResult]:
        table_name = self.__build_table_name(dataset_id)

        if await self.count_documents(dataset_id) == 0:
            return []

        store = await self.__get_store(table_name)

        docs_and_scores = await store.asimilarity_search_with_score_by_vector(
            embedding=query_embedding,
            k=limit,
        )

        results: List[VectorSearchResult] = []

        for document, distance_score in docs_and_scores:
            similarity_score = self.__distance_to_similarity(
                distance_score,
            )

            if (
                score_threshold is not None
                and similarity_score
                < score_threshold
            ):
                continue

            results.append(
                VectorSearchResult(
                    document=self.__to_vector_document(
                        dataset_id=dataset_id,
                        document=document,
                    ),
                    score=similarity_score,
                )
            )

        return results

    async def delete_dataset(self, dataset_id: UUID) -> None:
        table_name = self.__build_table_name(dataset_id)

        await self.__drop_table_if_exists(table_name)

        if table_name in self._stores:
            del self._stores[table_name]

    async def count_documents(self, dataset_id: UUID) -> int:
        table_name = self.__build_table_name(dataset_id)

        if not await self.__table_exists(table_name):
            return 0

        quoted_table_name = self.__quote_identifier(table_name)

        query = f"""
            SELECT COUNT(*)
            FROM {quoted_table_name}
        """

        async with self._db_context.engine.connect() as connection:
            result = await connection.exec_driver_sql(query)
            count = result.scalar_one()

        return int(count)

    async def __initialize_table(self, table_name: str) -> None:
        await self._pg_engine.ainit_vectorstore_table(
            table_name=table_name,
            vector_size=self._vector_size,
        )

    async def __get_store(self, table_name: str) -> PGVectorStore:
        if table_name not in self._stores:
            self._stores[table_name] = await PGVectorStore.create(
                engine=self._pg_engine,
                table_name=table_name,
                embedding_service=self._embedding_adapter,
                distance_strategy=DistanceStrategy.COSINE_DISTANCE,
            )

        return self._stores[table_name]

    async def __apply_hnsw_index(
        self,
        store: PGVectorStore,
        table_name: str,
    ) -> None:
        index = HNSWIndex()

        await store.aapply_vector_index(
            index=index,
        )

    async def __drop_table_if_exists(self, table_name: str) -> None:
        if not await self.__table_exists(table_name):
            return

        await self._pg_engine.adrop_table(table_name)

        if table_name in self._stores:
            del self._stores[table_name]

    async def __table_exists(self, table_name: str) -> bool:
        query = text(
            """
            SELECT EXISTS (
                SELECT 1
                FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_name = :table_name
            )
            """
        )

        async with self._db_context.engine.connect() as connection:
            result = await connection.execute(
                query,
                {"table_name": table_name},
            )

            return bool(result.scalar_one())

    def __build_table_name(self, dataset_id: UUID) -> str:
        dataset_suffix = str(dataset_id).replace("-", "_")

        return self.__sanitize_identifier(
            f"{self._table_prefix}_{dataset_suffix}"
        )

    def __sanitize_identifier(self, value: str) -> str:
        sanitized = re.sub(
            pattern=r"[^a-zA-Z0-9_]",
            repl="_",
            string=value,
        )

        sanitized = sanitized.lower()

        if not sanitized:
            raise ValueError("Database identifier cannot be empty.")

        if sanitized[0].isdigit():
            sanitized = f"v_{sanitized}"

        return sanitized

    def __quote_identifier(self, value: str) -> str:
        sanitized = self.__sanitize_identifier(value)

        return f'"{sanitized}"'

    def __sanitize_text(self, value: str) -> str:
        return value.replace("\x00", "")

    def __build_metadata(
        self,
        document: VectorDocument,
    ) -> dict:
        metadata = dict(document.metadata or {})

        metadata["dataset_id"] = str(document.dataset_id)
        metadata["chunk_index"] = document.chunk_index
        metadata["vector_document_id"] = str(document.id)

        return metadata

    def __to_vector_document(
        self,
        dataset_id: UUID,
        document: Document,
    ) -> VectorDocument:
        metadata = dict(document.metadata or {})

        chunk_index = int(
            metadata.get("chunk_index", 0)
        )

        vector_document_id = metadata.get("vector_document_id")

        if vector_document_id:
            return VectorDocument(
                id=UUID(vector_document_id),
                dataset_id=dataset_id,
                chunk_index=chunk_index,
                content=document.page_content,
                embedding=[],
                metadata=metadata,
            )

        return VectorDocument(
            dataset_id=dataset_id,
            chunk_index=chunk_index,
            content=document.page_content,
            embedding=[],
            metadata=metadata,
        )

    def __distance_to_similarity(
        self,
        distance_score: float,
    ) -> float:
        similarity = 1.0 - float(distance_score)

        if similarity < 0:
            return 0.0

        if similarity > 1:
            return 1.0

        return similarity

    def __batch(
        self,
        documents: List[VectorDocument],
        batch_size: int,
    ):
        for index in range(0, len(documents), batch_size):
            yield documents[index:index + batch_size]
