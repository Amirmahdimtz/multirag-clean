import tempfile
import unittest
from pathlib import Path
from uuid import UUID

from src.core.dataset.dataset_business import DatasetBusiness
from src.domain.enums.dataset_scope import DatasetScope
from src.domain.models.document_chunk import DocumentChunk
from src.infrastructure.database.db_context import DbContext
from src.infrastructure.embedding.embedding_service import EmbeddingService
from src.infrastructure.repositories.dataset_repository import DatasetRepository
from src.infrastructure.storage.file_storage_service import FileStorageService
from src.infrastructure.vector_store.persistent_vector_store_service import (
    PersistentVectorStoreService,
)


class InMemoryUpload:
    def __init__(
        self,
        filename: str,
        content: bytes,
        content_type: str = "text/plain",
    ) -> None:
        self.filename = filename
        self.content_type = content_type
        self._content = content

    async def read(self, size: int = -1) -> bytes:
        if size < 0:
            return self._content

        return self._content[:size]


class TextFileDocumentProcessor:
    def process_file(
        self,
        dataset_id: UUID,
        file_path: str,
    ) -> list[DocumentChunk]:
        content = Path(file_path).read_text(encoding="utf-8").strip()

        if not content:
            return []

        return [
            DocumentChunk(
                dataset_id=dataset_id,
                content=content,
                chunk_index=0,
                token_count=None,
                metadata={"source_file_path": file_path},
            )
        ]


class RAGPipelineIntegrationTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        root = Path(self.temp_dir.name)

        self.db_context = DbContext(
            database_url=f"sqlite+aiosqlite:///{root / 'integration.db'}",
        )
        await self.db_context.init_db()

        self.dataset_repository = DatasetRepository(self.db_context)
        self.vector_store = PersistentVectorStoreService(self.db_context)
        self.embedding_service = EmbeddingService(dimension=32)
        self.file_storage = FileStorageService(
            base_path=str(root / "storage"),
        )

        self.dataset_business = DatasetBusiness(
            dataset_repository=self.dataset_repository,
            file_storage_service=self.file_storage,
            document_processing_service=TextFileDocumentProcessor(),
            embedding_service=self.embedding_service,
            vector_store_service=self.vector_store,
            allowed_extensions=["txt"],
            max_file_size_mb=1,
            default_k_retrieval=5,
            default_score_threshold=0.0,
        )

    async def asyncTearDown(self) -> None:
        await self.db_context.engine.dispose()
        self.temp_dir.cleanup()

    async def test_upload_vectorize_and_search_round_trip(self) -> None:
        upload = InMemoryUpload(
            filename="knowledge.txt",
            content=(
                b"retrieval augmented generation combines retrieval "
                b"with language model generation"
            ),
        )

        dataset = await self.dataset_business.upload_dataset(
            name="integration-knowledge",
            file=upload,
            scope=DatasetScope.ADMIN,
        )

        self.assertTrue(
            self.file_storage.exists(dataset.storage_file_name)
        )
        self.assertFalse(dataset.is_vectorized)

        vector_count = await self.dataset_business.vectorize_dataset(
            dataset_id=dataset.id,
        )

        self.assertEqual(1, vector_count)

        persisted = await self.dataset_repository.get_by_id(dataset.id)
        self.assertIsNotNone(persisted)
        self.assertTrue(persisted.is_vectorized)
        self.assertEqual(
            self.embedding_service.provider_name,
            persisted.embedding_provider,
        )
        self.assertEqual(
            self.embedding_service.model_name,
            persisted.embedding_model,
        )
        self.assertEqual(
            self.embedding_service.dimension,
            persisted.embedding_dimension,
        )

        results = await self.dataset_business.search_dataset(
            dataset_id=dataset.id,
            query="retrieval generation",
        )

        self.assertEqual(1, len(results))
        self.assertIn(
            "retrieval augmented generation",
            results[0].document.content,
        )
        self.assertGreaterEqual(results[0].score, 0.0)
        self.assertLessEqual(results[0].score, 1.0)


if __name__ == "__main__":
    unittest.main()
