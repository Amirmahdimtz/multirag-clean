from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from src.application.common.controllers.base_controller import BaseController
from src.application.common.dtos.base_response_dto import BaseResponseDto
from src.application.security.api_key_dependencies import ApiKeyDependencies
from src.core.rag_system.rag_system_business import RAGSystemBusiness
from src.application.rag_system.dtos.create_rag_system_request_dto import (
    CreateRAGSystemRequestDto,
)
from src.application.rag_system.dtos.rag_search_response_dto import (
    RAGSearchResponseDto,
)
from src.application.rag_system.dtos.rag_search_result_dto import (
    RAGSearchResultDto,
)
from src.application.rag_system.dtos.rag_system_list_response_dto import (
    RAGSystemListResponseDto,
)
from src.application.rag_system.dtos.rag_system_response_dto import (
    RAGSystemResponseDto,
)
from src.application.rag_system.dtos.rag_system_single_response_dto import (
    RAGSystemSingleResponseDto,
)
from src.application.rag_system.dtos.ask_rag_system_request_dto import (
    AskRAGSystemRequestDto,
)
from src.application.rag_system.dtos.ask_rag_system_response_dto import (
    AskRAGSystemResponseDto,
)
from src.application.rag_system.dtos.ask_rag_system_data_dto import (
    AskRAGSystemDataDto,
)
from src.application.rag_system.dtos.rag_answer_context_dto import (
    RAGAnswerContextDto,
)


class RAGSystemController(BaseController):
    route_prefix = "/admin/rag-systems"

    def __init__(
        self,
        rag_system_business: RAGSystemBusiness,
        api_key_dependencies: ApiKeyDependencies,
    ) -> None:
        self.rag_system_business = rag_system_business
        self.api_key_dependencies = api_key_dependencies

    def api(self) -> APIRouter:
        router = APIRouter(
            prefix="",
            tags=["RAG Systems"],
            dependencies=[
                Depends(self.api_key_dependencies.require_admin_api_key),
            ],
            responses={404: {"description": "Not found"}},
        )

        @router.post(
            "",
            response_model=RAGSystemSingleResponseDto,
            status_code=status.HTTP_201_CREATED,
        )
        async def create_rag_system(
            dto: CreateRAGSystemRequestDto,
        ) -> RAGSystemSingleResponseDto:
            rag_system = await self.rag_system_business.create(
                name=dto.name,
                dataset_id=dto.dataset_id,
                description=dto.description,
            )

            return RAGSystemSingleResponseDto(
                success=True,
                message="RAG system created successfully",
                data=self.__to_response_dto(rag_system),
            )

        @router.get(
            "",
            response_model=RAGSystemListResponseDto,
        )
        async def get_all_rag_systems() -> RAGSystemListResponseDto:
            rag_systems = await self.rag_system_business.get_all()

            return RAGSystemListResponseDto(
                success=True,
                message="RAG systems fetched successfully",
                data=[
                    self.__to_response_dto(rag_system)
                    for rag_system in rag_systems
                ],
            )

        @router.get(
            "/{rag_system_id}",
            response_model=RAGSystemSingleResponseDto,
        )
        async def get_rag_system(
            rag_system_id: UUID,
        ) -> RAGSystemSingleResponseDto:
            rag_system = await self.rag_system_business.get_by_id(
                rag_system_id,
            )

            return RAGSystemSingleResponseDto(
                success=True,
                message="RAG system fetched successfully",
                data=self.__to_response_dto(rag_system),
            )

        @router.delete(
            "/{rag_system_id}",
            response_model=BaseResponseDto,
        )
        async def delete_rag_system(
            rag_system_id: UUID,
        ) -> BaseResponseDto:
            await self.rag_system_business.delete(rag_system_id)

            return BaseResponseDto(
                success=True,
                message="RAG system deleted successfully",
                data=None,
            )

        @router.get(
            "/{rag_system_id}/search",
            response_model=RAGSearchResponseDto,
        )
        async def search_rag_system(
            rag_system_id: UUID,
            query: str,
            limit: int | None = Query(
                default=None,
                ge=1,
                le=20,
            ),
            score_threshold: float | None = Query(
                default=None,
                ge=0,
                le=1,
            ),
        ) -> RAGSearchResponseDto:
            results = await self.rag_system_business.search(
                rag_system_id=rag_system_id,
                query=query,
                limit=limit,
                score_threshold=score_threshold,
            )

            return RAGSearchResponseDto(
                success=True,
                message="RAG search completed successfully",
                data=[
                    RAGSearchResultDto(
                        chunk_index=result.document.chunk_index,
                        content=result.document.content,
                        score=result.score,
                    )
                    for result in results
                ],
            )

        @router.post(
            "/{rag_system_id}/ask",
            response_model=AskRAGSystemResponseDto,
        )
        async def ask_rag_system(
            rag_system_id: UUID,
            dto: AskRAGSystemRequestDto,
        ) -> AskRAGSystemResponseDto:
            result = await self.rag_system_business.answer_question(
                rag_system_id=rag_system_id,
                question=dto.question,
                limit=dto.limit,
                score_threshold=dto.score_threshold,
            )

            return AskRAGSystemResponseDto(
                success=True,
                message="RAG answer generated successfully",
                data=AskRAGSystemDataDto(
                    answer=result.answer,
                    contexts=[
                        RAGAnswerContextDto(
                            chunk_index=context.chunk_index,
                            content=context.content,
                            score=context.score,
                        )
                        for context in result.contexts
                    ],
                ),
            )

        return router

    def __to_response_dto(self, rag_system) -> RAGSystemResponseDto:
        return RAGSystemResponseDto(
            id=rag_system.id,
            name=rag_system.name,
            dataset_id=rag_system.dataset_id,
            description=rag_system.description,
        )
