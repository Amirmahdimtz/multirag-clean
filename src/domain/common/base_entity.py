from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4


class BaseEntity:
    def __init__(
        self,
        id: Optional[UUID] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ) -> None:
        self.id = id or uuid4()
        self.created_at = created_at or datetime.now(datetime.timezone.utc)
        self.updated_at = updated_at or datetime.now(datetime.timezone.utc)

    def touch(self) -> None:
        self.updated_at = datetime.now(datetime.timezone.utc)
