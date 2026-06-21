from pydantic import BaseModel
from uuid import UUID


class DatasetResponseDto(BaseModel):
    id: UUID
    name: str
    file_name: str
    is_vectorized: bool
