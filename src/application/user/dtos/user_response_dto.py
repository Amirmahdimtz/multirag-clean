from pydantic import BaseModel
from uuid import UUID


class UserResponseDto(BaseModel):
    id: UUID
    username: str
