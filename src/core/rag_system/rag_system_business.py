from typing import List
from uuid import UUID

from src.core.rag_system.rag_answer_result import RAGAnswerResult
from src.core.exceptions.bad_request_exception import BadRequestException
from src.core.exceptions.not_found_exception import NotFoundException
from src.domain.models.dataset import Dataset
from src.domain.models.rag_system import RAGSystem
from src.core.rag_system.rag_answer_context_result import (
    RAGAnswerContextResult,
)
from src.core.rag_system.rag_answer_result import RAGAnswerResult


class RAGSystemBusiness:
    def __init__(
        self,
        rag_system_repository,
        dataset_repository,
        embedding_service,
        vector_store_service,
        llm_factory,
    ) -> None:
        self.rag_system_repository = rag_system_repository
        self.dataset_repository = dataset_repository
        self.embedding_service = embedding_service
        self.vector_store_service = vector_store_service
        self.llm_factory = llm_factory

    async def create(
        self,
        name: str,
        dataset_id: UUID,
        description: str | None = None,
    ) -> RAGSystem:
        dataset = await self.dataset_repository.get_by_id(
            Dataset,
            dataset_id,
        )

        if dataset is None:
            raise NotFoundException("Dataset not found")

        if not dataset.is_vectorized:
            raise BadRequestException(
                "Dataset must be vectorized before creating a RAG system"
            )

        if self.vector_store_service.count_documents(dataset.id) == 0:
            raise BadRequestException(
                "Vector index not found. Please vectorize dataset again."
            )

        rag_system = RAGSystem(
            name=name,
            dataset_id=dataset.id,
            description=description,
        )

        return await self.rag_system_repository.add(rag_system)

    async def get_all(self) -> List[RAGSystem]:
        return await self.rag_system_repository.get_all()

    async def get_by_id(self, rag_system_id: UUID) -> RAGSystem:
        rag_system = await self.rag_system_repository.get_by_id(
            RAGSystem,
            rag_system_id,
        )

        if rag_system is None:
            raise NotFoundException("RAG system not found")

        return rag_system

    async def delete(self, rag_system_id: UUID) -> None:
        rag_system = await self.get_by_id(rag_system_id)
        await self.rag_system_repository.delete(rag_system)

    async def search(
        self,
        rag_system_id: UUID,
        query: str,
        limit: int = 5,
    ):
        rag_system = await self.get_by_id(rag_system_id)

        if self.vector_store_service.count_documents(rag_system.dataset_id) == 0:
            raise BadRequestException(
                "Vector index not found. Please vectorize dataset again."
            )

        query_embedding = self.embedding_service.embed_text(query)

        return self.vector_store_service.similarity_search(
            dataset_id=rag_system.dataset_id,
            query_embedding=query_embedding,
            limit=limit,
        )

    async def answer_question(
        self,
        rag_system_id: UUID,
        question: str,
        limit: int = 5,
    ) -> RAGAnswerResult:
        search_results = await self.search(
            rag_system_id=rag_system_id,
            query=question,
            limit=limit,
        )

        contexts = [
            result.document.content
            for result in search_results
        ]

        rag_llm = self.llm_factory.create_rag_llm()

        answer = await rag_llm.generate(
            question=question,
            contexts=contexts,
        )

        return RAGAnswerResult(
            answer=answer,
            contexts=[
                RAGAnswerContextResult(
                    chunk_index=result.document.chunk_index,
                    content=result.document.content,
                    score=result.score,
                )
                for result in search_results
            ],
        )
