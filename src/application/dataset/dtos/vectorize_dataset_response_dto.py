from typing import Optional

from src.application.common.dtos.base_response_dto import BaseResponseDto
from src.application.dataset.dtos.vectorize_dataset_data_dto import (
    VectorizeDatasetDataDto,
)


class VectorizeDatasetResponseDto(BaseResponseDto):
    data: Optional[VectorizeDatasetDataDto] = None
