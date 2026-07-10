from uuid import UUID

from pydantic import BaseModel


class RAGAccessUserDto(BaseModel):
    id: UUID
    username: str
