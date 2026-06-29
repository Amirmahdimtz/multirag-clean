from typing import List, Optional

from src.application.common.dtos.base_response_dto import BaseResponseDto
from src.application.dataset.dtos.vector_search_result_dto import (
    VectorSearchResultDto,
)


class VectorSearchResponseDto(BaseResponseDto):
    data: Optional[List[VectorSearchResultDto]] = None
