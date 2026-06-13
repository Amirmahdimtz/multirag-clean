
from typing import Optional

from src.application.common.dtos.base_response_dto import BaseResponseDto
from src.application.health.dtos.health_data_dto import HealthDataDto


class HealthResponseDto(BaseResponseDto):
    data: Optional[HealthDataDto] = None
