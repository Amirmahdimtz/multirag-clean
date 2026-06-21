from typing import Optional

from sqlalchemy import Boolean, Enum as SqlEnum, String
from sqlalchemy.orm import Mapped, mapped_column

from src.domain.common.base_entity import BaseEntity
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

    dataset_type: Mapped[DatasetType] = mapped_column(
        SqlEnum(
            DatasetType,
            name="dataset_type",
            native_enum=False,
            values_callable=lambda enum: [item.value for item in enum],
        ),
        nullable=False,
        default=DatasetType.UNKNOWN,
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

    def mark_as_vectorized(self) -> None:
        self.is_vectorized = True
        self.touch()
