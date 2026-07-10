from uuid import UUID

from fastapi import APIRouter, Depends, status

from src.application.common.controllers.base_controller import BaseController
from src.application.common.dtos.base_response_dto import BaseResponseDto
from src.application.security.api_key_dependencies import ApiKeyDependencies
from src.application.rag_access.dtos.rag_access_rag_system_dto import (
    RAGAccessRAGSystemDto,
)
from src.application.rag_access.dtos.rag_access_request_dto import (
    RAGAccessRequestDto,
)
from src.application.rag_access.dtos.rag_access_response_dto import (
    RAGAccessResponseDto,
)
from src.application.rag_access.dtos.rag_access_user_dto import (
    RAGAccessUserDto,
)
from src.core.rag_access.rag_access_business import RAGAccessBusiness


class RAGAccessController(BaseController):
    route_prefix = "/admin/rag_access"

    def __init__(
        self,
        rag_access_business: RAGAccessBusiness,
        api_key_dependencies: ApiKeyDependencies,
    ) -> None:
        self.rag_access_business = rag_access_business
        self.api_key_dependencies = api_key_dependencies

    def api(self) -> APIRouter:
        router = APIRouter(
            prefix="",
            tags=["RAG Access"],
            dependencies=[
                Depends(self.api_key_dependencies.require_admin_api_key),
            ],
            responses={404: {"description": "Not found"}},
        )

        @router.post(
            "",
            response_model=BaseResponseDto,
            status_code=status.HTTP_201_CREATED,
        )
        async def grant_rag_access(
            dto: RAGAccessRequestDto,
        ) -> BaseResponseDto:
            rag_access = await self.rag_access_business.grant_access(
                user_id=dto.user_id,
                rag_system_id=dto.rag_system_id,
            )

            return BaseResponseDto(
                success=True,
                message="RAG access granted successfully",
                data=RAGAccessResponseDto(
                    id=rag_access.id,
                    user_id=rag_access.user_id,
                    rag_system_id=rag_access.rag_system_id,
                ),
            )

        @router.get(
            "/users",
            response_model=BaseResponseDto,
        )
        async def get_users_by_rag_system(
            rag_system_id: UUID,
        ) -> BaseResponseDto:
            users = await self.rag_access_business.get_users_by_rag_system(
                rag_system_id=rag_system_id,
            )

            return BaseResponseDto(
                success=True,
                message="Users fetched successfully",
                data=[
                    RAGAccessUserDto(
                        id=user.id,
                        username=user.username,
                    )
                    for user in users
                ],
            )

        @router.get(
            "/rag_systems",
            response_model=BaseResponseDto,
        )
        async def get_rag_systems_by_user(
            user_id: UUID,
        ) -> BaseResponseDto:
            rag_systems = await self.rag_access_business.get_rag_systems_by_user(
                user_id=user_id,
            )

            return BaseResponseDto(
                success=True,
                message="RAG systems fetched successfully",
                data=[
                    RAGAccessRAGSystemDto(
                        id=rag_system.id,
                        name=rag_system.name,
                        dataset_id=rag_system.dataset_id,
                        description=rag_system.description,
                    )
                    for rag_system in rag_systems
                ],
            )

        @router.delete(
            "",
            response_model=BaseResponseDto,
        )
        async def revoke_rag_access(
            dto: RAGAccessRequestDto,
        ) -> BaseResponseDto:
            await self.rag_access_business.revoke_access(
                user_id=dto.user_id,
                rag_system_id=dto.rag_system_id,
            )

            return BaseResponseDto(
                success=True,
                message="RAG access revoked successfully",
                data=None,
            )

        return router
