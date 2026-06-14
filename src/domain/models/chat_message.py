from datetime import datetime
from typing import Optional
from uuid import UUID

from src.domain.common.base_entity import BaseEntity
from src.domain.enums.message_role import MessageRole


class ChatMessage(BaseEntity):
    def __init__(
        self,
        session_id: UUID,
        role: MessageRole,
        content: str,
        id: Optional[UUID] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ) -> None:
        super().__init__(
            id=id,
            created_at=created_at,
            updated_at=updated_at,
        )

        self.session_id = session_id
        self.role = role
        self.content = content
