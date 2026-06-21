from typing import List, Optional

from src.application.common.dtos.base_response_dto import BaseResponseDto
from src.application.dataset.dtos.document_chunk_preview_dto import (
    DocumentChunkPreviewDto,
)


class DocumentChunkPreviewResponseDto(BaseResponseDto):
    data: Optional[List[DocumentChunkPreviewDto]] = None
