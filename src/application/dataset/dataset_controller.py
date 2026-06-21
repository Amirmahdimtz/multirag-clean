from fastapi import APIRouter, UploadFile, File, Form

from src.application.common.controllers.base_controller import BaseController
from src.application.common.dtos.base_response_dto import BaseResponseDto
from src.application.dataset.dtos.dataset_response_dto import DatasetResponseDto
from src.core.dataset.dataset_business import DatasetBusiness


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

        return router
