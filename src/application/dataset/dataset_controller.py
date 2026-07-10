from uuid import UUID

from fastapi import APIRouter, UploadFile, File, Form, Depends, Query, Response

from src.domain.models.dataset import Dataset
from src.application.common.controllers.base_controller import BaseController
from src.application.common.dtos.base_response_dto import BaseResponseDto
from src.application.dataset.dtos.dataset_response_dto import DatasetResponseDto
from src.application.security.api_key_dependencies import ApiKeyDependencies
from src.core.dataset.dataset_business import DatasetBusiness
from src.core.exceptions.not_found_exception import NotFoundException
from src.application.dataset.dtos.document_chunk_preview_dto import (
    DocumentChunkPreviewDto,
)
from src.application.dataset.dtos.document_chunk_preview_response_dto import (
    DocumentChunkPreviewResponseDto,
)
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


class DatasetController(BaseController):
    route_prefix = "/admin/datasets"

    def __init__(
        self,
        dataset_business: DatasetBusiness,
        api_key_dependencies: ApiKeyDependencies,
    ) -> None:
        self.dataset_business = dataset_business
        self.api_key_dependencies = api_key_dependencies

    def api(self) -> APIRouter:
        router = APIRouter(
            prefix="",
            tags=["Admin Datasets"],
            dependencies=[
                Depends(self.api_key_dependencies.require_admin_api_key),
            ],
            responses={404: {"description": "Not found"}},
        )

        @router.post("/upload")
        async def upload_dataset(
            name: str = Form(...),
            file: UploadFile = File(...),
            admin_id: UUID | None = Form(default=None),
            expertise: str | None = Form(default=None),
        ) -> BaseResponseDto:
            dataset = await self.dataset_business.upload_dataset(
                name=name,
                file=file,
                admin_id=admin_id,
                expertise=expertise,
            )

            return BaseResponseDto(
                success=True,
                message="Dataset uploaded successfully",
                data=self.__dataset_response(dataset),
            )

        @router.get("/")
        async def get_all() -> BaseResponseDto:
            datasets = await self.dataset_business.get_all()

            return BaseResponseDto(
                success=True,
                message="Datasets fetched",
                data=[
                    self.__dataset_response(dataset)
                    for dataset in datasets
                ],
            )

        @router.post(
            "/{dataset_id}/vectorize",
            response_model=VectorizeDatasetResponseDto,
        )
        async def vectorize_dataset(dataset_id: UUID):
            vector_count = await self.dataset_business.vectorize_dataset(dataset_id)

            return VectorizeDatasetResponseDto(
                success=True,
                message="Dataset vectorized successfully",
                data=VectorizeDatasetDataDto(
                    vector_count=vector_count,
                ),
            )

        @router.get(
            "/{dataset_id}/search",
            response_model=VectorSearchResponseDto,
        )
        async def search_dataset(
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
        ):
            results = await self.dataset_business.search_dataset(
                dataset_id=dataset_id,
                query=query,
                limit=limit,
                score_threshold=score_threshold,
            )

            return VectorSearchResponseDto(
                success=True,
                message="Vector search completed successfully",
                data=[
                    VectorSearchResultDto(
                        chunk_index=result.document.chunk_index,
                        content=result.document.content,
                        score=result.score,
                    )
                    for result in results
                ],
            )

        @router.get(
            "/{dataset_id}/chunks/preview",
            response_model=DocumentChunkPreviewResponseDto,
        )
        async def preview_chunks(dataset_id: UUID, limit: int = 5):
            chunks = await self.dataset_business.preview_chunks(
                dataset_id=dataset_id,
                limit=limit,
            )

            return DocumentChunkPreviewResponseDto(
                success=True,
                message="Document chunks preview fetched successfully",
                data=[
                    DocumentChunkPreviewDto(
                        chunk_index=chunk.chunk_index,
                        content=chunk.content,
                        character_count=len(chunk.content),
                    )
                    for chunk in chunks
                ],
            )

        @router.get("/{dataset_id}/download")
        async def download_dataset(
            dataset_id: UUID,
        ):
            dataset = await self.dataset_business.get_by_id(dataset_id)

            if dataset.content is None:
                raise NotFoundException("Dataset content not found")

            return Response(
                content=dataset.content,
                media_type=dataset.content_type or "application/octet-stream",
                headers={
                    "Content-Disposition": f'attachment; filename="{dataset.file_name}"'
                },
            )

        @router.get("/{dataset_id}/filename")
        async def get_dataset_filename(
            dataset_id: UUID,
        ) -> BaseResponseDto:
            dataset = await self.dataset_business.get_by_id(dataset_id)

            return BaseResponseDto(
                success=True,
                message="Dataset filename fetched successfully",
                data={
                    "filename": dataset.file_name,
                },
            )

        return router

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
