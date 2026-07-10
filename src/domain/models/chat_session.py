from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy import DateTime, Enum as SqlEnum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import Uuid

from src.domain.common.base_entity import BaseEntity
from src.domain.enums.llm_type import LLMType


class ChatSession(BaseEntity):
    __tablename__ = "chat_sessions"

    user_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    llm_type: Mapped[LLMType] = mapped_column(
        SqlEnum(
            LLMType,
            name="llm_type",
            native_enum=False,
            values_callable=lambda enum: [item.value for item in enum],
        ),
        nullable=False,
    )

    rag_system_id: Mapped[Optional[UUID]] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("rag_systems.id"),
        nullable=True,
        index=True,
    )

    user_dataset_id: Mapped[Optional[UUID]] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("datasets.id"),
        nullable=True,
        index=True,
    )

    last_active_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    def __init__(
        self,
        user_id: UUID,
        name: str,
        llm_type: LLMType,
        rag_system_id: Optional[UUID] = None,
        user_dataset_id: Optional[UUID] = None,
    ) -> None:
        super().__init__()

        self.user_id = user_id
        self.name = name
        self.llm_type = llm_type
        self.rag_system_id = rag_system_id
        self.user_dataset_id = user_dataset_id
        self.last_active_at = datetime.now(timezone.utc)

    def mark_as_active(self) -> None:
        self.last_active_at = datetime.now(timezone.utc)
        self.touch()
