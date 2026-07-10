from typing import Optional
from uuid import UUID

from sqlalchemy import Float, LargeBinary

from sqlalchemy import Boolean, Enum as SqlEnum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import Uuid

from src.domain.common.base_entity import BaseEntity
from src.domain.enums.dataset_scope import DatasetScope
from src.domain.enums.dataset_type import DatasetType


class Dataset(BaseEntity):
    __tablename__ = "datasets"

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )

    file_name: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )

    storage_file_name: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
    )

    dataset_type: Mapped[DatasetType] = mapped_column(
        SqlEnum(
            DatasetType,
            name="dataset_type",
            native_enum=False,
            values_callable=lambda enum: [
                item.value for item in enum
            ],
        ),
        nullable=False,
        default=DatasetType.UNKNOWN,
    )

    scope: Mapped[DatasetScope] = mapped_column(
        SqlEnum(
            DatasetScope,
            name="dataset_scope",
            native_enum=False,
            values_callable=lambda enum: [item.value for item in enum],
        ),
        nullable=False,
        default=DatasetScope.ADMIN,
        index=True,
    )

    owner_user_id: Mapped[Optional[UUID]] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True,
        index=True,
    )

    admin_id: Mapped[Optional[UUID]] = mapped_column(
        Uuid(as_uuid=True),
        nullable=True,
        index=True,
    )

    expertise: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )

    file_size_mb: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )

    content: Mapped[Optional[bytes]] = mapped_column(
        LargeBinary,
        nullable=True,
    )

    content_type: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )

    is_vectorized: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )

    embedding_provider: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )

    embedding_model: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
    )

    embedding_dimension: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
    )

    def mark_as_vectorized(
        self,
        embedding_provider: str,
        embedding_model: str,
        embedding_dimension: int,
    ) -> None:
        self.is_vectorized = True
        self.embedding_provider = embedding_provider
        self.embedding_model = embedding_model
        self.embedding_dimension = embedding_dimension
        self.touch()
