from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, Query, UploadFile

from src.application.common.controllers.base_controller import BaseController
from src.application.common.dtos.base_response_dto import BaseResponseDto
from src.application.dataset.dtos.dataset_response_dto import DatasetResponseDto
from src.application.dataset.dtos.vector_search_response_dto import (
    VectorSearchResponseDto,
)
from src.application.dataset.dtos.vector_search_result_dto import (
    VectorSearchResultDto,
)
from src.application.dataset.dtos.vectorize_dataset_data_dto import (
    VectorizeDatasetDataDto,
)
from src.application.dataset.dtos.vectorize_dataset_response_dto import (
    VectorizeDatasetResponseDto,
)
from src.application.security.api_key_dependencies import ApiKeyDependencies
from src.core.dataset.user_dataset_business import UserDatasetBusiness
from src.core.exceptions.unauthorized_exception import UnauthorizedException
from src.core.security.authenticated_api_key import AuthenticatedApiKey
from src.domain.models.dataset import Dataset


class UserDatasetController(BaseController):
    route_prefix = "/user/datasets"

    def __init__(
        self,
        user_dataset_business: UserDatasetBusiness,
        api_key_dependencies: ApiKeyDependencies,
    ) -> None:
        self.user_dataset_business = user_dataset_business
        self.api_key_dependencies = api_key_dependencies

    def api(self) -> APIRouter:
        router = APIRouter(
            prefix="",
            tags=["User Datasets"],
            responses={404: {"description": "Not found"}},
        )

        @router.post("/upload")
        async def upload_user_dataset(
            name: str = Form(...),
            file: UploadFile = File(...),
            authenticated_api_key: AuthenticatedApiKey = Depends(
                self.api_key_dependencies.require_user_api_key
            ),
        ) -> BaseResponseDto:
            user_id = self.__get_authenticated_user_id(authenticated_api_key)

            dataset = await self.user_dataset_business.upload_user_dataset(
                user_id=user_id,
                name=name,
                file=file,
            )

            return BaseResponseDto(
                success=True,
                message="User dataset uploaded successfully",
                data=self.__dataset_response(dataset),
            )

        @router.get("/")
        async def get_user_datasets(
            authenticated_api_key: AuthenticatedApiKey = Depends(
                self.api_key_dependencies.require_user_api_key
            ),
        ) -> BaseResponseDto:
            user_id = self.__get_authenticated_user_id(authenticated_api_key)

            datasets = await self.user_dataset_business.get_user_datasets(
                user_id=user_id,
            )

            return BaseResponseDto(
                success=True,
                message="User datasets fetched successfully",
                data=[self.__dataset_response(dataset)
                      for dataset in datasets],
            )

        @router.post(
            "/{dataset_id}/vectorize",
            response_model=VectorizeDatasetResponseDto,
        )
        async def vectorize_user_dataset(
            dataset_id: UUID,
            authenticated_api_key: AuthenticatedApiKey = Depends(
                self.api_key_dependencies.require_user_api_key
            ),
        ):
            user_id = self.__get_authenticated_user_id(authenticated_api_key)

            vector_count = await self.user_dataset_business.vectorize_user_dataset(
                user_id=user_id,
                dataset_id=dataset_id,
            )

            return VectorizeDatasetResponseDto(
                success=True,
                message="User dataset vectorized successfully",
                data=VectorizeDatasetDataDto(
                    vector_count=vector_count,
                ),
            )

        @router.get(
            "/{dataset_id}/search",
            response_model=VectorSearchResponseDto,
        )
        async def search_user_dataset(
            dataset_id: UUID,
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
            authenticated_api_key: AuthenticatedApiKey = Depends(
                self.api_key_dependencies.require_user_api_key
            ),
        ):
            user_id = self.__get_authenticated_user_id(authenticated_api_key)

            results = await self.user_dataset_business.search_user_dataset(
                user_id=user_id,
                dataset_id=dataset_id,
                query=query,
                limit=limit,
                score_threshold=score_threshold,
            )

            return VectorSearchResponseDto(
                success=True,
                message="User dataset search completed successfully",
                data=[
                    VectorSearchResultDto(
                        chunk_index=result.document.chunk_index,
                        content=result.document.content,
                        score=result.score,
                    )
                    for result in results
                ],
            )

        @router.delete("/{dataset_id}")
        async def delete_user_dataset(
            dataset_id: UUID,
            authenticated_api_key: AuthenticatedApiKey = Depends(
                self.api_key_dependencies.require_user_api_key
            ),
        ) -> BaseResponseDto:
            user_id = self.__get_authenticated_user_id(authenticated_api_key)

            await self.user_dataset_business.delete_user_dataset(
                user_id=user_id,
                dataset_id=dataset_id,
            )

            return BaseResponseDto(
                success=True,
                message="User dataset deleted successfully",
                data=None,
            )

        return router

    def __get_authenticated_user_id(
        self,
        authenticated_api_key: AuthenticatedApiKey,
    ) -> UUID:
        if authenticated_api_key.user_id is None:
            raise UnauthorizedException("User API key is required")

        return authenticated_api_key.user_id

    def __dataset_response(self, dataset: Dataset) -> DatasetResponseDto:
        return DatasetResponseDto(
            id=dataset.id,
            name=dataset.name,
            file_name=dataset.file_name,
            scope=dataset.scope,
            owner_user_id=dataset.owner_user_id,
            is_vectorized=dataset.is_vectorized,
            embedding_provider=dataset.embedding_provider,
            embedding_model=dataset.embedding_model,
            embedding_dimension=dataset.embedding_dimension,
            dataset_type=dataset.dataset_type,
            content_type=dataset.content_type,
            admin_id=dataset.admin_id,
            expertise=dataset.expertise,
            file_size_mb=dataset.file_size_mb,
        )
