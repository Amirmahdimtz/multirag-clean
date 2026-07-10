from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from src.domain.enums.dataset_scope import DatasetScope
from src.domain.enums.dataset_type import DatasetType


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
    dataset_type: DatasetType
    content_type: Optional[str] = None
    admin_id: Optional[UUID] = None
    expertise: Optional[str] = None
    file_size_mb: Optional[float] = None
