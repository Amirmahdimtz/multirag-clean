from typing import Optional

from src.application.common.dtos.base_response_dto import BaseResponseDto
from src.application.rag_system.dtos.ask_rag_system_data_dto import (
    AskRAGSystemDataDto,
)


class AskRAGSystemResponseDto(BaseResponseDto):
    data: Optional[AskRAGSystemDataDto] = None
