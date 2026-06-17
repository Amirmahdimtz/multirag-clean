from pydantic import BaseModel
from typing import Optional
from uuid import UUID


class UserResponseDto(BaseModel):
    id: UUID
    username: str
