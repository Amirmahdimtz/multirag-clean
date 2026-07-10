from uuid import UUID

from pydantic import BaseModel


class RAGAccessResponseDto(BaseModel):
    id: UUID
    user_id: UUID
    rag_system_id: UUID
