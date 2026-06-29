from typing import Optional

from src.application.common.dtos.base_response_dto import BaseResponseDto
from src.application.rag_system.dtos.rag_system_response_dto import (
    RAGSystemResponseDto,
)


class RAGSystemSingleResponseDto(BaseResponseDto):
    data: Optional[RAGSystemResponseDto] = None
