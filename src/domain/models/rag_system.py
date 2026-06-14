from datetime import datetime
from typing import Optional
from uuid import UUID

from src.domain.common.base_entity import BaseEntity


class RAGSystem(BaseEntity):
    def __init__(
        self,
        name: str,
        dataset_id: UUID,
        description: Optional[str] = None,
        id: Optional[UUID] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ) -> None:
        super().__init__(
            id=id,
            created_at=created_at,
            updated_at=updated_at,
        )

        self.name = name
        self.description = description
        self.dataset_id = dataset_id
