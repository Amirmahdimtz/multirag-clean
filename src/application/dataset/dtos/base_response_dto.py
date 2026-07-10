from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from src.domain.enums.dataset_scope import DatasetScope


class DatasetResponseDto(BaseModel):
    id: UUID
    name: str
    file_name: str
    scope: DatasetScope
    owner_user_id: Optional[UUID] = None
    is_vectorized: bool
    embedding_provider: Optional[str] = None
    embedding_model: Optional[str] = None
    embedding_dimension: Optional[int] = None
