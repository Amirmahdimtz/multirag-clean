from uuid import UUID

from pydantic import BaseModel


class RAGAccessRequestDto(BaseModel):
    user_id: UUID
    rag_system_id: UUID
