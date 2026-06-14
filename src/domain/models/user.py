from datetime import datetime
from typing import Optional
from uuid import UUID

from src.domain.common.base_entity import BaseEntity


class User(BaseEntity):
    def __init__(
        self,
        username: str,
        id: Optional[UUID] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ) -> None:
        super().__init__(
            id=id,
            created_at=created_at,
            updated_at=updated_at,
        )

        self.username = username
