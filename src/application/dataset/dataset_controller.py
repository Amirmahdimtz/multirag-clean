from uuid import UUID

from fastapi import APIRouter, UploadFile, File, Form

from src.application.common.controllers.base_controller import BaseController
from src.application.common.dtos.base_response_dto import BaseResponseDto
from src.application.dataset.dtos.dataset_response_dto import DatasetResponseDto
from src.core.dataset.dataset_business import DatasetBusiness
from src.application.dataset.dtos.document_chunk_preview_dto import (
    DocumentChunkPreviewDto,
)
from src.application.dataset.dtos.document_chunk_preview_response_dto import (
    DocumentChunkPreviewResponseDto,
)


class DatasetController(BaseController):
    route_prefix = "/datasets"

    def __init__(self, dataset_business: DatasetBusiness) -> None:
        self.dataset_business = dataset_business

    def api(self) -> APIRouter:
        router = APIRouter(
            prefix="",
            tags=["Datasets"],
            responses={404: {"description": "Not found"}},
        )

        @router.post("/upload")
        async def upload_dataset(
            name: str = Form(...),
            file: UploadFile = File(...),
        ) -> BaseResponseDto:
            dataset = await self.dataset_business.upload_dataset(
                name=name,
                file=file,
            )

            return BaseResponseDto(
                success=True,
                message="Dataset uploaded successfully",
                data=DatasetResponseDto(
                    id=dataset.id,
                    name=dataset.name,
                    file_name=dataset.file_name,
                    is_vectorized=dataset.is_vectorized,
                ),
            )

        @router.get("/")
        async def get_all() -> BaseResponseDto:
            datasets = await self.dataset_business.get_all()

            return BaseResponseDto(
                success=True,
                message="Datasets fetched",
                data=[
                    DatasetResponseDto(
                        id=dataset.id,
                        name=dataset.name,
                        file_name=dataset.file_name,
                        is_vectorized=dataset.is_vectorized,
                    )
                    for dataset in datasets
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

        return router
