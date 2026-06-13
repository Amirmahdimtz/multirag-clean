from fastapi import APIRouter

from src.application.common.controllers.base_controller import BaseController
from src.application.health.dtos.health_data_dto import HealthDataDto
from src.application.health.dtos.health_info_data_dto import HealthInfoDataDto
from src.application.health.dtos.health_info_response_dto import HealthInfoResponseDto
from src.application.health.dtos.health_response_dto import HealthResponseDto
from src.infrastructure.config.config_reader import ConfigReader


class HealthController(BaseController):
    route_prefix = "/health"

    def __init__(self, config_reader: ConfigReader) -> None:
        self.config_reader = config_reader

    def api(self) -> APIRouter:
        router = APIRouter(
            prefix="",
            tags=["Health"],
            responses={404: {"description": "Not found"}},
        )

        @router.get("/", response_model=HealthResponseDto)
        async def health_check() -> HealthResponseDto:
            data = HealthDataDto(
                status="ok",
                application_name=self.config_reader.get(
                    "application.name",
                    "MultiRAG Clean",
                ),
                version=self.config_reader.get(
                    "application.version",
                    "0.1.0",
                ),
            )

            return HealthResponseDto(
                success=True,
                message="Health checked successfully",
                data=data,
            )

        @router.get("/info", response_model=HealthInfoResponseDto)
        async def health_info() -> HealthInfoResponseDto:
            data = HealthInfoDataDto(
                project="MultiRAG",
                architecture="Layered Architecture + Dependency Injection",
                python_version="3.10",
            )

            return HealthInfoResponseDto(
                success=True,
                message="Project information fetched successfully",
                data=data,
            )

        return router
