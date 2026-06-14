from datetime import datetime
from typing import Optional
from uuid import UUID

from src.domain.common.base_entity import BaseEntity
from src.domain.enums.dataset_type import DatasetType


class Dataset(BaseEntity):
    def __init__(
        self,
        name: str,
        file_name: str,
        dataset_type: DatasetType,
        content_type: Optional[str] = None,
        is_vectorized: bool = False,
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
        self.file_name = file_name
        self.dataset_type = dataset_type
        self.content_type = content_type
        self.is_vectorized = is_vectorized

    def mark_as_vectorized(self) -> None:
        self.is_vectorized = True
        self.touch()
