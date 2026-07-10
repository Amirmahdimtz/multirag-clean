from uuid import UUID

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import Uuid

from src.domain.common.base_entity import BaseEntity


class RAGAccess(BaseEntity):
    __tablename__ = "rag_accesses"

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "rag_system_id",
            name="uq_rag_access_user_rag_system",
        ),
    )

    user_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey(
            "users.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    rag_system_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey(
            "rag_systems.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )
