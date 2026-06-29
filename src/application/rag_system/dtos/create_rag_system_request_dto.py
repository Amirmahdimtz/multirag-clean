from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class CreateRAGSystemRequestDto(BaseModel):
    name: str
    dataset_id: UUID
    description: Optional[str] = None
