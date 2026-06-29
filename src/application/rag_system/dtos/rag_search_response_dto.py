from typing import List, Optional

from src.application.common.dtos.base_response_dto import BaseResponseDto
from src.application.rag_system.dtos.rag_search_result_dto import (
    RAGSearchResultDto,
)


class RAGSearchResponseDto(BaseResponseDto):
    data: Optional[List[RAGSearchResultDto]] = None
