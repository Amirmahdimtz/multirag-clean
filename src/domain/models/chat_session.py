from datetime import datetime
from typing import Optional
from uuid import UUID

from src.domain.common.base_entity import BaseEntity
from src.domain.enums.llm_type import LLMType


class ChatSession(BaseEntity):
    def __init__(
        self,
        user_id: UUID,
        name: str,
        llm_type: LLMType,
        rag_system_id: Optional[UUID] = None,
        id: Optional[UUID] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        last_active_at: Optional[datetime] = None,
    ) -> None:
        super().__init__(
            id=id,
            created_at=created_at,
            updated_at=updated_at,
        )

        self.user_id = user_id
        self.name = name
        self.llm_type = llm_type
        self.rag_system_id = rag_system_id
        self.last_active_at = last_active_at or datetime.now(
            datetime.timezone.utc)

    def mark_as_active(self) -> None:
        self.last_active_at = datetime.now(datetime.timezone.utc)
        self.touch()
