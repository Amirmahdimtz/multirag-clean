from typing import List
from uuid import UUID

from src.core.contracts.repositories.i_dataset_repository import (
    IDatasetRepository,
)
from src.core.contracts.repositories.i_rag_system_repository import (
    IRAGSystemRepository,
)
from src.core.contracts.services.i_embedding_service import (
    IEmbeddingService,
)
from src.core.contracts.services.i_vector_store_service import (
    IVectorStoreService,
)
from src.core.exceptions.bad_request_exception import (
    BadRequestException,
)
from src.core.exceptions.not_found_exception import (
    NotFoundException,
)
from src.core.llm.llm_factory import LLMFactory
from src.core.rag_system.rag_answer_context_result import (
    RAGAnswerContextResult,
)
from src.core.rag_system.rag_answer_result import (
    RAGAnswerResult,
)
from src.domain.enums.dataset_scope import DatasetScope
from src.domain.models.rag_system import RAGSystem
from src.domain.models.vector_search_result import (
    VectorSearchResult,
)


class RAGSystemBusiness:
    def __init__(
        self,
        rag_system_repository: IRAGSystemRepository,
        dataset_repository: IDatasetRepository,
        embedding_service: IEmbeddingService,
        vector_store_service: IVectorStoreService,
        default_k_retrieval: int,
        default_score_threshold: float | None,
        llm_factory: LLMFactory,
    ) -> None:
        self.rag_system_repository = (
            rag_system_repository
        )

        self.dataset_repository = (
            dataset_repository
        )

        self.embedding_service = (
            embedding_service
        )

        self.vector_store_service = (
            vector_store_service
        )

        self.default_k_retrieval = int(
            default_k_retrieval
        )

        if self.default_k_retrieval <= 0:
            raise ValueError(
                "rag.k_retrieval "
                "must be greater than zero"
            )
        self.default_score_threshold = (
            None
            if default_score_threshold is None
            else float(
                default_score_threshold
            )
        )

        self.__validate_score_threshold(
            self.default_score_threshold
        )

        self.llm_factory = llm_factory

    async def create(
        self,
        name: str,
        dataset_id: UUID,
        description: str | None = None,
    ) -> RAGSystem:
        dataset = (
            await self.dataset_repository.get_by_id(
                dataset_id
            )
        )

        if dataset is None:
            raise NotFoundException(
                "Dataset not found"
            )

        if dataset.scope != DatasetScope.ADMIN:
            raise BadRequestException(
                "Only admin datasets can be used "
                "to create RAG systems."
            )

        if not dataset.is_vectorized:
            raise BadRequestException(
                "Dataset must be vectorized before "
                "creating a RAG system"
            )

        self.__ensure_dataset_embedding_is_compatible(
            dataset
        )

        document_count = (
            await self.vector_store_service
            .count_documents(
                dataset.id
            )
        )

        if document_count == 0:
            raise BadRequestException(
                "Vector index not found. "
                "Please vectorize dataset again."
            )

        rag_system = RAGSystem(
            name=name,
            dataset_id=dataset.id,
            description=description,
        )

        return (
            await self.rag_system_repository.add(
                rag_system
            )
        )

    async def get_all(
        self,
    ) -> List[RAGSystem]:
        return (
            await self.rag_system_repository.get_all()
        )

    async def get_by_id(
        self,
        rag_system_id: UUID,
    ) -> RAGSystem:
        rag_system = (
            await self.rag_system_repository
            .get_by_id(
                rag_system_id
            )
        )

        if rag_system is None:
            raise NotFoundException(
                "RAG system not found"
            )

        return rag_system

    async def delete(
        self,
        rag_system_id: UUID,
    ) -> None:
        rag_system = await self.get_by_id(
            rag_system_id
        )

        await self.rag_system_repository.delete(
            rag_system
        )

    async def search(
        self,
        rag_system_id: UUID,
        query: str,
        limit: int | None = None,
        score_threshold: float | None = None,
    ) -> List[VectorSearchResult]:
        rag_system = await self.get_by_id(
            rag_system_id
        )

        dataset = (
            await self.dataset_repository.get_by_id(
                rag_system.dataset_id
            )
        )

        if dataset is None:
            raise NotFoundException(
                "Dataset not found"
            )

        if dataset.scope != DatasetScope.ADMIN:
            raise BadRequestException(
                "RAG systems can only search "
                "admin datasets."
            )

        if not dataset.is_vectorized:
            raise BadRequestException(
                "Dataset is not vectorized yet"
            )

        self.__ensure_dataset_embedding_is_compatible(
            dataset
        )

        document_count = (
            await self.vector_store_service
            .count_documents(
                rag_system.dataset_id
            )
        )

        if document_count == 0:
            raise BadRequestException(
                "Vector index not found. "
                "Please vectorize dataset again."
            )

        query_embedding = (
            self.embedding_service.embed_text(
                query
            )
        )

        effective_limit = (
            self.default_k_retrieval
            if limit is None
            else limit
        )

        effective_score_threshold = (
            self.default_score_threshold
            if score_threshold is None
            else score_threshold
        )

        self.__validate_score_threshold(
            effective_score_threshold
        )

        return (
            await self.vector_store_service
            .similarity_search(
                dataset_id=(
                    rag_system.dataset_id
                ),
                query_embedding=(
                    query_embedding
                ),
                limit=effective_limit,
                score_threshold=(
                    effective_score_threshold
                ),
            )
        )

    async def answer_question(
        self,
        rag_system_id: UUID,
        question: str,
        limit: int | None = None,
        score_threshold: float | None = None,
    ) -> RAGAnswerResult:
        search_results = await self.search(
            rag_system_id=rag_system_id,
            query=question,
            limit=limit,
            score_threshold=score_threshold,
        )

        contexts = self.__build_llm_contexts(
            search_results
        )

        rag_llm = (
            self.llm_factory.create_rag_llm()
        )

        answer = await rag_llm.generate(
            question=question,
            contexts=contexts,
        )

        return RAGAnswerResult(
            answer=answer,
            contexts=[
                RAGAnswerContextResult(
                    chunk_index=(
                        result.document
                        .chunk_index
                    ),
                    content=(
                        result.document
                        .content
                    ),
                    score=result.score,
                )
                for result in search_results
            ],
        )

    def __build_llm_contexts(
        self,
        search_results: List[
            VectorSearchResult
        ],
    ) -> List[str]:
        contexts: List[str] = []

        for result in search_results:
            document_content = (
                result.document.content
            )

            metadata = (
                result.document.metadata
                or {}
            )

            answer = str(
                metadata.get(
                    "answer",
                    "",
                )
                or ""
            ).strip()

            if answer:
                document_content = f"""
Question:
{document_content}

Answer:
{answer}
""".strip()

            context = f"""
[chunk: {result.document.chunk_index}]
{document_content}
""".strip()

            contexts.append(
                context
            )

        return contexts

    def __ensure_dataset_embedding_is_compatible(
        self,
        dataset,
    ) -> None:
        if (
            dataset.embedding_provider is None
            or dataset.embedding_model is None
            or dataset.embedding_dimension is None
        ):
            raise BadRequestException(
                "Dataset embedding metadata is "
                "missing. Please vectorize this "
                "dataset again with the active "
                "embedding provider."
            )

        if (
            dataset.embedding_provider
            != self.embedding_service.provider_name
        ):
            raise BadRequestException(
                "Dataset was vectorized with "
                f"embedding provider "
                f"'{dataset.embedding_provider}', "
                "but active provider is "
                f"'{self.embedding_service.provider_name}'. "
                "Please vectorize this dataset "
                "again."
            )

        if (
            dataset.embedding_model
            != self.embedding_service.model_name
        ):
            raise BadRequestException(
                "Dataset was vectorized with "
                f"embedding model "
                f"'{dataset.embedding_model}', "
                "but active model is "
                f"'{self.embedding_service.model_name}'. "
                "Please vectorize this dataset "
                "again."
            )

        if (
            dataset.embedding_dimension
            != self.embedding_service.dimension
        ):
            raise BadRequestException(
                "Dataset was vectorized with "
                f"dimension "
                f"{dataset.embedding_dimension}, "
                "but active embedding dimension is "
                f"{self.embedding_service.dimension}. "
                "Please vectorize this dataset "
                "again."
            )

    def __validate_score_threshold(
        self,
        score_threshold: float | None,
    ) -> None:
        if score_threshold is None:
            return

        if (
            score_threshold < 0
            or score_threshold > 1
        ):
            raise BadRequestException(
                "score_threshold must be "
                "between 0 and 1."
            )
