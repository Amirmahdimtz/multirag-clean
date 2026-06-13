from typing import Optional

from src.application.common.dtos.base_response_dto import BaseResponseDto
from src.application.health.dtos.health_info_data_dto import HealthInfoDataDto


class HealthInfoResponseDto(BaseResponseDto):
    data: Optional[HealthInfoDataDto] = None
