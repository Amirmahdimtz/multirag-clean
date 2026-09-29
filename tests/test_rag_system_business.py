import unittest
from types import SimpleNamespace
from uuid import uuid4

from src.core.exceptions.bad_request_exception import BadRequestException
from src.core.exceptions.not_found_exception import NotFoundException
from src.core.rag_system.rag_system_business import RAGSystemBusiness
from src.domain.enums.dataset_scope import DatasetScope
from src.domain.models.vector_document import VectorDocument
from src.domain.models.vector_search_result import VectorSearchResult


class FakeRAGSystemRepository:
    def __init__(self) -> None:
        self.items = {}

    async def add(self, rag_system):
        if getattr(rag_system, "id", None) is None:
            rag_system.id = uuid4()
        self.items[rag_system.id] = rag_system
        return rag_system

    async def get_all(self):
        return list(self.items.values())

    async def get_by_id(self, rag_system_id):
        return self.items.get(rag_system_id)

    async def update(self, rag_system):
        self.items[rag_system.id] = rag_system
        return rag_system

    async def delete(self, rag_system):
        self.items.pop(rag_system.id, None)


class FakeDatasetRepository:
    def __init__(self, dataset=None) -> None:
        self.dataset = dataset

    async def get_by_id(self, dataset_id):
        if self.dataset is not None and self.dataset.id == dataset_id:
            return self.dataset
        return None


class FakeEmbeddingService:
    provider_name = "fake"
    model_name = "hash-embedding"
    dimension = 8

    def embed_text(self, text):
        return [1.0] + [0.0] * (self.dimension - 1)


class FakeVectorStore:
    def __init__(self, count=1, results=None) -> None:
        self.count = count
        self.results = results or []
        self.last_search = None

    async def count_documents(self, dataset_id):
        return self.count

    async def similarity_search(
        self,
        dataset_id,
        query_embedding,
        limit,
        score_threshold=None,
    ):
        self.last_search = {
            "dataset_id": dataset_id,
            "query_embedding": query_embedding,
            "limit": limit,
            "score_threshold": score_threshold,
        }
        return self.results


class FakeLLMFactory:
    def create_rag_llm(self):
        raise AssertionError("LLM generation is not used in these tests")


def make_dataset(
    *,
    scope=DatasetScope.ADMIN,
    is_vectorized=True,
    embedding_provider="fake",
    embedding_model="hash-embedding",
    embedding_dimension=8,
):
    return SimpleNamespace(
        id=uuid4(),
        scope=scope,
        is_vectorized=is_vectorized,
        embedding_provider=embedding_provider,
        embedding_model=embedding_model,
        embedding_dimension=embedding_dimension,
    )


class RAGSystemBusinessTests(unittest.IsolatedAsyncioTestCase):
    def build_business(self, dataset, *, vector_count=1, results=None):
        repository = FakeRAGSystemRepository()
        vector_store = FakeVectorStore(
            count=vector_count,
            results=results,
        )
        business = RAGSystemBusiness(
            rag_system_repository=repository,
            dataset_repository=FakeDatasetRepository(dataset),
            embedding_service=FakeEmbeddingService(),
            vector_store_service=vector_store,
            default_k_retrieval=4,
            default_score_threshold=0.25,
            llm_factory=FakeLLMFactory(),
        )
        return business, repository, vector_store

    async def test_create_rejects_missing_dataset(self) -> None:
        business, _, _ = self.build_business(None)

        with self.assertRaises(NotFoundException):
            await business.create(
                name="missing",
                dataset_id=uuid4(),
            )

    async def test_create_rejects_user_owned_dataset(self) -> None:
        dataset = make_dataset(scope=DatasetScope.USER)
        business, _, _ = self.build_business(dataset)

        with self.assertRaises(BadRequestException):
            await business.create(
                name="invalid",
                dataset_id=dataset.id,
            )

    async def test_create_requires_vectorized_dataset(self) -> None:
        dataset = make_dataset(is_vectorized=False)
        business, _, _ = self.build_business(dataset)

        with self.assertRaises(BadRequestException):
            await business.create(
                name="not-vectorized",
                dataset_id=dataset.id,
            )

    async def test_create_requires_vector_index_documents(self) -> None:
        dataset = make_dataset()
        business, _, _ = self.build_business(
            dataset,
            vector_count=0,
        )

        with self.assertRaises(BadRequestException):
            await business.create(
                name="missing-index",
                dataset_id=dataset.id,
            )

    async def test_create_persists_valid_rag_system(self) -> None:
        dataset = make_dataset()
        business, repository, _ = self.build_business(dataset)

        rag_system = await business.create(
            name="knowledge-base",
            dataset_id=dataset.id,
            description="Reusable test system",
        )

        self.assertEqual(dataset.id, rag_system.dataset_id)
        self.assertEqual("knowledge-base", rag_system.name)
        self.assertIn(rag_system.id, repository.items)

    async def test_search_rejects_embedding_mismatch(self) -> None:
        dataset = make_dataset(embedding_model="different-model")
        business, repository, _ = self.build_business(dataset)

        rag_system = SimpleNamespace(
            id=uuid4(),
            dataset_id=dataset.id,
        )
        repository.items[rag_system.id] = rag_system

        with self.assertRaises(BadRequestException):
            await business.search(
                rag_system_id=rag_system.id,
                query="hello",
            )

    async def test_search_uses_defaults_and_returns_results(self) -> None:
        dataset = make_dataset()
        document = VectorDocument(
            dataset_id=dataset.id,
            chunk_index=0,
            content="retrieval augmented generation",
            embedding=[1.0] + [0.0] * 7,
        )
        expected = [
            VectorSearchResult(
                document=document,
                score=0.9,
            )
        ]
        business, repository, vector_store = self.build_business(
            dataset,
            results=expected,
        )

        rag_system = SimpleNamespace(
            id=uuid4(),
            dataset_id=dataset.id,
        )
        repository.items[rag_system.id] = rag_system

        actual = await business.search(
            rag_system_id=rag_system.id,
            query="retrieval",
        )

        self.assertEqual(expected, actual)
        self.assertEqual(4, vector_store.last_search["limit"])
        self.assertEqual(
            0.25,
            vector_store.last_search["score_threshold"],
        )
        self.assertEqual(
            FakeEmbeddingService().embed_text("retrieval"),
            vector_store.last_search["query_embedding"],
        )


if __name__ == "__main__":
    unittest.main()
