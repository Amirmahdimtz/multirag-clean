from typing import List, Optional

from src.application.common.dtos.base_response_dto import BaseResponseDto
from src.application.rag_system.dtos.rag_system_response_dto import (
    RAGSystemResponseDto,
)


class RAGSystemListResponseDto(BaseResponseDto):
    data: Optional[List[RAGSystemResponseDto]] = None
